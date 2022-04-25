from typing import Optional, Dict
import ctypes
import pathlib
import logging
import glm
from pydear.scene.camera import Camera
from pydear.scene.gizmo import Gizmo
from ..formats import pmd_loader, gltf_loader, vpd_loader, pmx_loader
from ..formats import tpose
from ..formats.transform import Transform
from ..formats.pose import Pose, Motion
from ..formats.humanoid_bones import HumanoidBone
from .node import Node
from .skeleton import Skeleton
LOGGER = logging.getLogger(__name__)


class Scene:
    '''
    モデル一体分のシーングラフ
    '''

    def __init__(self, name: str) -> None:
        self.name = name
        # scene
        self.root = Node(-1, '__root__', Transform.identity())
        self.is_mmd = False
        self.mask = None
        self.gizmo = Gizmo()
        self.skeleton = None
        self.selected: Optional[Node] = None

        # GUI check box
        self.visible_mesh = (ctypes.c_bool * 1)(False)
        self.visible_gizmo = (ctypes.c_bool * 1)(True)
        self.visible_skeleton = (ctypes.c_bool * 1)(False)

    def _setup_model(self):
        self.root.initialize(glm.mat4())
        self.root.calc_skinning(glm.mat4())
        self.skeleton = Skeleton(self.root)
        self.root.calc_skinning(glm.mat4())
        self.humanoid_node_map = {node.humanoid_bone: node for node,
                                  _ in self.root.traverse_node_and_parent() if node.humanoid_bone}

    def load_model(self, path: pathlib.Path):
        match path.suffix.lower():
            case '.pmd':
                self.load_pmd(path)
                self.is_mmd = True
            case '.pmx':
                self.load_pmx(path)
                self.is_mmd = True
            case '.glb' | '.vrm':
                self.load_glb(path)
                self.is_mmd = False
            case _:
                raise NotImplementedError()

    def load_pmd(self, path: pathlib.Path):
        pmd = pmd_loader.Pmd(path.read_bytes())
        LOGGER.debug(pmd)
        from .builder import pmd_builder
        self.root = pmd_builder.build(pmd)
        self._setup_model()

    def load_pmx(self, path: pathlib.Path):
        pmx = pmx_loader.Pmx(path.read_bytes())
        LOGGER.debug(pmx)
        from .builder import pmx_builder
        self.root = pmx_builder.build(pmx)
        self._setup_model()

    def load_glb(self, path: pathlib.Path):
        gltf = gltf_loader.Gltf.load_glb(path.read_bytes())
        LOGGER.debug(gltf)
        from .builder import gltf_builder
        self.root = gltf_builder.build(gltf)
        self._setup_model()

    def create_model(self):
        from .builder import create
        self.root = create.create()
        self._setup_model()

    def create_tpose_from(self, scene: 'Scene'):
        def copy_tree(src: Node, dst: Node):

            for s in src.children:
                d = Node(s.index, s.name, s.init_trs,
                         humanoid_bone=s.humanoid_bone)

                dst.add_child(d)
                copy_tree(s, d)

        self.root = Node(-1, '__root__', Transform.identity())
        copy_tree(scene.root, self.root)
        self._setup_model()

        if scene.is_mmd:
            node_pos_map: Dict[HumanoidBone, glm.vec3] = {
                node.humanoid_bone: node.world_matrix[3].xyz for node, _ in scene.root.traverse_node_and_parent() if node.humanoid_bone}

            hips = self.root.find_humanoid_bone(HumanoidBone.hips)
            assert hips
            spine = self.root.find_humanoid_bone(HumanoidBone.spine)
            assert spine
            spine.init_trs = spine.init_trs._replace(
                translation=node_pos_map[HumanoidBone.hips.spine]-node_pos_map[HumanoidBone.hips])
            hips.name = 'hips'
            hips.add_child(spine, insert=True)
            hips.humanoid_tail = spine

        # tpose
        tpose.make_tpose(self.root)
        delta_map = tpose.pose_to_init(self.root)
        tpose.local_axis_fit_world(self.root)
        # restore pose
        for node, _ in self.root.traverse_node_and_parent():
            delta = delta_map.get(node)
            if delta:
                node.delta = delta
        self._setup_model()

    def render(self, camera: Camera):
        if self.visible_mesh[0]:
            if root := self.root:
                self.render_node(camera, root)

        if self.visible_gizmo[0]:
            self.gizmo.begin(camera.x, camera.y, camera.left, camera.view.matrix,
                             camera.projection.matrix, camera.get_mouse_ray(camera.x, camera.y))
            # self.gizmo.axis(1)
            self.gizmo.ground_mark()

            for bone, _ in self.root.traverse_node_and_parent():
                if bone.humanoid_bone:
                    assert bone.humanoid_tail
                    # bone
                    self.gizmo.bone_head_tail(bone.humanoid_bone.name,
                                              bone.world_matrix[3].xyz, bone.humanoid_tail.world_matrix[3].xyz, glm.vec3(
                                                  0, 0, 1),
                                              is_selected=bone == self.selected)
                    # axis
                    self.gizmo.matrix = (
                        bone.world_matrix * glm.mat4(bone.local_axis))
                    self.gizmo.color = glm.vec4(1, 0, 0, 1)
                    self.gizmo.line(glm.vec3(0), glm.vec3(0.02, 0, 0))
                    self.gizmo.color = glm.vec4(0, 1, 0, 1)
                    self.gizmo.line(glm.vec3(0), glm.vec3(0, 0.02, 0))
                    self.gizmo.color = glm.vec4(0, 0, 1, 1)
                    self.gizmo.line(glm.vec3(0), glm.vec3(0, 0, 0.02))

            self.gizmo.end()

        if self.skeleton and self.visible_skeleton[0]:
            self.skeleton.renderer.render(camera)

    def render_node(self, camera: Camera, node: Node):
        if node.renderer:
            node.renderer.render(camera, node)

        for child in node.children:
            self.render_node(camera, child)

    def set_pose(self, pose: Pose):
        if not self.root:
            return

        self.root.clear_pose()

        def conv(bone: vpd_loader.BonePose):
            t = bone.transform.reverse_z()
            return t

        # assign pose to node hierarchy
        for bone in pose.bones:
            if bone.humanoid_bone:
                node = self.humanoid_node_map.get(bone.humanoid_bone)
                if node:
                    if self.mask and not self.mask(bone.humanoid_bone):
                        continue
                    node.pose = conv(bone)

        self.root.calc_skinning(glm.mat4())
