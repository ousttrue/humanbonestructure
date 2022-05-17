from typing import Optional, Dict
import ctypes
import pathlib
import logging
import glm
from pydear.scene.camera import Camera
from pydear.utils.mouse_event import MouseEvent, MouseInput
from pydear.gizmo.gizmo import Gizmo
from pydear import imgui as ImGui
from ..formats.bvh import bvh_parser
from ..formats import pmd_loader, gltf_loader, pmx_loader
from ..humanoid import tpose
from ..humanoid.transform import Transform
from ..humanoid.pose import Pose, BonePose
from ..humanoid.humanoid_bones import HumanoidBone
from ..humanoid.humanoid_skeleton import HumanoidSkeleton
from .node import Node


LOGGER = logging.getLogger(__name__)
RED = glm.vec4(1, 0, 0, 1)
GREEN = glm.vec4(0, 1, 0, 1)
BLUE = glm.vec4(0, 0, 1, 1)


class Scene:
    '''
    モデル一体分のシーングラフ
    '''

    def __init__(self, mouse_event: MouseEvent) -> None:
        self.mouse_event = mouse_event
        self.camera = Camera(distance=8, y=-0.8)
        self.camera.bind_mouse_event(self.mouse_event)
        # scene
        self.root = Node('__root__', Transform.identity())
        self.is_mmd = False
        self.gizmo = Gizmo()
        self.selected: Optional[Node] = None
        self.tpose_delta_map: Dict[HumanoidBone, glm.quat] = {}
        self.humanoid_node_map: Dict[HumanoidBone, Node] = {}
        self.node_shape_map = {}

        # GUI check box
        self.visible_mesh = (ctypes.c_bool * 1)(False)
        self.visible_gizmo = (ctypes.c_bool * 1)(True)

    def get_root(self):
        return self.root

    def get_selected(self):
        return self.selected

    def set_selected(self, selected):
        self.selected = selected

    def show_option(self):
        ImGui.Checkbox('gizmo', self.visible_gizmo)
        ImGui.SameLine()
        ImGui.Checkbox('mesh', self.visible_mesh)

    def _setup_model(self):
        self.root.init_human_bones()
        self.root.calc_bind_matrix(glm.mat4())
        self.root.calc_world_matrix(glm.mat4())
        self.humanoid_node_map = {node.humanoid_bone: node for node,
                                  _ in self.root.traverse_node_and_parent(only_human_bone=True)}

        # # make tpose for pose conversion
        # tpose.make_tpose(self.root, is_inverted_pelvis=self.is_mmd)
        # self.tpose_delta_map: Dict[HumanoidBone, glm.quat] = {node.humanoid_bone: node.pose.rotation if node.pose else glm.quat(
        # ) for node, _ in self.root.traverse_node_and_parent(only_human_bone=True)}
        # tpose.local_axis_fit_world(self.root)
        # self.root.clear_pose()
        # self.root.calc_world_matrix(glm.mat4())
        # # tpose.pose_to_delta(scene.root)

        from ..gui.bone_shape import BoneShape
        self.node_shape_map.clear()
        for node, shape in BoneShape.from_root(self.root, self.gizmo).items():
            self.node_shape_map[node] = shape

    def load(self, value):
        from ..formats.bvh.bvh_parser import Bvh
        from ..formats.pmd_loader import Pmd
        from ..formats.pmx_loader import Pmx
        from ..formats.gltf_loader import Gltf
        match value:
            case Bvh() as bvh:
                from .builder import bvh_builder
                self.root = bvh_builder.build(bvh)
                self._setup_model()
            case Pmd() as pmd:
                from .builder import pmd_builder
                self.root = pmd_builder.build(pmd)
                self._setup_model()
            case Pmx() as pmx:
                from .builder import pmx_builder
                self.root = pmx_builder.build(pmx)
                self._setup_model()
            case Gltf() as gltf:
                from .builder import gltf_builder
                self.root = gltf_builder.build(gltf)
                self._setup_model()
            case Node() as root:
                self.root = root
                self._setup_model()
            case HumanoidSkeleton() as skeleton:
                self.root = skeleton.to_node()
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

    def render(self, w: int, h: int):
        mouse_input = self.mouse_event.last_input
        assert(mouse_input)
        self.camera.projection.resize(w, h)

        if self.visible_mesh[0]:
            if root := self.root:
                self.render_node(self.camera, root)

        if self.visible_gizmo[0]:
            self.gizmo.process(self.camera, mouse_input.x, mouse_input.y)

    def render_node(self, camera: Camera, node: Node):
        if node.renderer:
            node.renderer.render(camera, node)

        for child in node.children:
            self.render_node(camera, child)

    def set_pose(self, pose: Optional[Pose]):
        if not self.root or not self.humanoid_node_map:
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

        # sync to gizmo
        for node, shape in self.node_shape_map.items():
            shape.matrix.set(node.world_matrix * glm.mat4(node.local_axis))
