from typing import Optional, Callable
import ctypes
import pathlib
import logging
import glm
from pydear.scene.camera import Camera
from ..formats import pmd_loader, gltf_loader, vpd_loader, pmx_loader
from ..formats.humanoid_bones import HumanoidBone
from ..formats import tpose
from ..formats.transform import Transform
from .node import Node
from .gizmo import Gizmo
from .skeleton import Skeleton
LOGGER = logging.getLogger(__name__)


class Scene:
    '''
    モデル一体分のシーングラフ
    '''

    def __init__(self) -> None:
        # scene
        self.root = Node(-1, '__root__', Transform.identity())
        self.gizmo = Gizmo()
        self.skeleton = None
        # GUI check box
        self.visible_mesh = (ctypes.c_bool * 1)(True)
        self.visible_gizmo = (ctypes.c_bool * 1)(True)
        self.visible_skeleton = (ctypes.c_bool * 1)(True)

    def _setup_model(self):
        self.root.initialize(glm.mat4())
        self.root.calc_skinning(glm.mat4())
        self.skeleton = Skeleton(self.root)
        self._skinning()

    def _skinning(self):
        self.root.calc_skinning(glm.mat4())
        self.gizmo.update(self.root)

    def load_model(self, path: pathlib.Path):
        match path.suffix.lower():
            case '.pmd':
                self.load_pmd(path)
            case '.pmx':
                self.load_pmx(path)
            case '.glb' | '.vrm':
                self.load_glb(path)
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
        self.root = create.create_hand()
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
            self.gizmo.render(camera)

        if self.skeleton and self.visible_skeleton[0]:
            self.skeleton.renderer.render(camera)

    def render_node(self, camera: Camera, node: Node):
        if node.renderer:
            node.renderer.render(camera, node)

        for child in node.children:
            self.render_node(camera, child)

    def load_vpd(self, vpd: Optional[vpd_loader.Vpd], mask: Optional[Callable[[HumanoidBone], bool]] = None):
        if not self.root:
            return

        for node, _ in self.root.traverse_node_and_parent():
            node.pose = None

        self.vpd = vpd
        LOGGER.debug(self.vpd)

        humanoid_node_map = {node.humanoid_bone: node for node,
                             _ in self.root.traverse_node_and_parent() if node.humanoid_bone}

        def conv(bone: vpd_loader.BonePose):
            t = bone.transform.reverse_z()
            return t

        # assign pose to node hierarchy
        if self.vpd:
            for bone in self.vpd.bones:
                humanoid_bone = pmd_loader.BONE_HUMANOID_MAP.get(bone.name)
                if humanoid_bone:
                    node = humanoid_node_map.get(humanoid_bone)
                    if node:
                        if not mask or mask(humanoid_bone):
                            node.pose = conv(bone)

        self._skinning()
