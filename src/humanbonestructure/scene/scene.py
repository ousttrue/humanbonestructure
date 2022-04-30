from typing import Optional, Dict
import ctypes
import pathlib
import logging
import glm
from pydear.scene.camera import Camera
from pydear.scene.gizmo import Gizmo
from ..formats import pmd_loader, gltf_loader, pmx_loader, bvh_parser
from ..formats import tpose
from ..formats.transform import Transform
from ..formats.pose import Pose, BonePose
from ..formats.humanoid_bones import HumanoidBone
from .node import Node
from .skeleton import Skeleton
LOGGER = logging.getLogger(__name__)

RED = glm.vec4(1, 0, 0, 1)
GREEN = glm.vec4(0, 1, 0, 1)
BLUE = glm.vec4(0, 0, 1, 1)


class Scene:
    '''
    モデル一体分のシーングラフ
    '''

    def __init__(self, name: str) -> None:
        self.name = name
        # scene
        self.root = Node('__root__', Transform.identity())
        self.is_mmd = False
        self.gizmo = Gizmo()
        self.skeleton = None
        self.selected: Optional[Node] = None
        self.tpose_delta_map: Dict[HumanoidBone, glm.quat] = {}

        # GUI check box
        self.visible_mesh = (ctypes.c_bool * 1)(False)
        self.visible_gizmo = (ctypes.c_bool * 1)(True)
        self.visible_skeleton = (ctypes.c_bool * 1)(False)

        from ..eventproperty import OptionalEventProperty
        self.pose_changed = OptionalEventProperty[Pose]()

    def _setup_model(self):
        self.root.init_human_bones()
        self.root.calc_bind_matrix(glm.mat4())
        self.root.calc_world_matrix(glm.mat4())
        self.skeleton = Skeleton(self.root)
        self.root.calc_world_matrix(glm.mat4())
        self.humanoid_node_map = {node.humanoid_bone: node for node,
                                  _ in self.root.traverse_node_and_parent(only_human_bone=True)}

        # make tpose for pose conversion
        tpose.make_tpose(self.root, is_inverted_pelvis=self.is_mmd)
        self.tpose_delta_map: Dict[HumanoidBone, glm.quat] = {node.humanoid_bone: node.pose.rotation if node.pose else glm.quat(
        ) for node, _ in self.root.traverse_node_and_parent(only_human_bone=True)}
        tpose.local_axis_fit_world(self.root)
        self.root.clear_pose()
        self.root.calc_world_matrix(glm.mat4())
        # tpose.pose_to_delta(scene.root)

    def load(self, value):
        from ..formats.bvh_parser import Bvh
        match value:
            case Bvh() as bvh:
                from .builder import bvh_builder
                self.root = bvh_builder.build(bvh)
                self._setup_model()
            case None:
                self.root = Node('__root__', Transform.identity())
                self.skeleton = None
            case _:
                raise NotImplementedError(value)

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

    def load_bvh(self, path: pathlib.Path) -> bvh_parser.Bvh:
        '''
        BVH をロードしてヒエラルキーを Scene に構築する

        return parsed Bvh
        '''
        bvh = bvh_parser.from_path(path)
        LOGGER.debug(bvh)
        from .builder import bvh_builder
        self.root = bvh_builder.build(bvh)
        self._setup_model()
        return bvh

    def create_model(self):
        from .builder import strict_tpose
        self.root = strict_tpose.create()
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

            # bone gizmo
            selected = None
            for bone, _ in self.root.traverse_node_and_parent(only_human_bone=True):
                assert bone.humanoid_bone
                assert bone.humanoid_tail
                # bone
                if self.gizmo.bone_head_tail(bone.humanoid_bone.name,
                                             bone.world_matrix[3].xyz, bone.humanoid_tail.world_matrix[3].xyz, glm.vec3(
                                                 0, 0, 1),
                                             is_selected=(bone == self.selected)):
                    selected = bone

                # axis
                self.gizmo.matrix = (
                    bone.world_matrix * glm.mat4(bone.local_axis))
                self.gizmo.color = RED
                self.gizmo.line(glm.vec3(0), glm.vec3(0.02, 0, 0))
                self.gizmo.color = GREEN
                self.gizmo.line(glm.vec3(0), glm.vec3(0, 0.02, 0))
                self.gizmo.color = BLUE
                self.gizmo.line(glm.vec3(0), glm.vec3(0, 0, 0.02))

            if selected:
                LOGGER.debug(f'selected: {selected}')
                self.selected = selected

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

        # assign pose to node hierarchy
        if pose and pose.bones:
            for bone in pose.bones:
                if bone.humanoid_bone:
                    node = self.humanoid_node_map.get(bone.humanoid_bone)
                    if node:
                        node.pose = bone.transform
                    else:
                        pass
                        # raise RuntimeError()
                else:
                    raise RuntimeError()

        self.root.calc_world_matrix(glm.mat4())

        #
        # raise TPose相対ポーズ
        #
        if self.pose_changed.callbacks:
            pose = self.root.create_relative_pose(self.tpose_delta_map)
            self.pose_changed.set(pose)
