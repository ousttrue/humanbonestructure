from typing import Optional, List
import pathlib
import logging
import glm
from pydear.scene.camera import Camera
from ..formats import pmd_loader, gltf_loader, vpd_loader, pmx_loader
from .node import Node
from .gizmo import Gizmo
LOGGER = logging.getLogger(__name__)


class Scene:
    '''
    モデル一体分のシーングラフ
    '''

    def __init__(self) -> None:
        # scene
        self.nodes: List[Node] = []
        self.roots: List[Node] = []
        self.enable_draw_skinning = False
        # model gizmo
        self.gizmo = Gizmo()

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

    def _setup_model(self):
        for root in self.roots:
            root.initialize()
            root.calc_skinning(glm.mat4())

        self.gizmo.update(self.nodes)

    def load_pmd(self, path: pathlib.Path):
        self.nodes.clear()
        self.roots.clear()

        pmd = pmd_loader.Pmd(path.read_bytes())
        LOGGER.debug(pmd)

        from .builder import pmd_builder
        pmd_builder.build(self, pmd)

        self._setup_model()

    def load_pmx(self, path: pathlib.Path):
        self.nodes.clear()
        self.roots.clear()

        pmx = pmx_loader.Pmx(path.read_bytes())
        LOGGER.debug(pmx)

        from .builder import pmx_builder
        pmx_builder.build(self, pmx)

        self._setup_model()

    def load_glb(self, path: pathlib.Path):
        self.nodes.clear()
        self.roots.clear()

        gltf = gltf_loader.Gltf.load_glb(path.read_bytes())
        LOGGER.debug(gltf)

        from .builder import gltf_builder
        gltf_builder.build(self, gltf)

        self._setup_model()

    def create_model(self):
        from .builder import create
        create.create_scene(self)

        self._setup_model()

    def render(self, camera: Camera):
        # render
        if self.enable_draw_skinning:
            for root in self.roots:
                self.render_node(camera, root)

        self.gizmo.render(camera)

    def render_node(self, camera: Camera, node: Node):
        if node.renderer:
            node.renderer.render(camera, node)

        for child in node.children:
            self.render_node(camera, child)

    def load_vpd(self, vpd: Optional[vpd_loader.Vpd]):
        # clear
        for node in self.nodes:
            node.pose = None

        # self.vpd = Vpd(pkgutil.get_data('humanbonestructure', 'assets/Pose/右手グー.vpd'))
        self.vpd = vpd
        LOGGER.debug(self.vpd)

        humanoid_node_map = {node.humanoid_bone: node for node in self.nodes}

        # assign pose to node hierarchy
        if self.vpd:
            for bone in self.vpd.bones:
                humanoid_bone = pmd_loader.BONE_HUMANOID_MAP.get(bone.name)
                if humanoid_bone:
                    node = humanoid_node_map.get(humanoid_bone)
                    if node and node.humanoid_bone:
                        # Handより祖先に適用しない(mask)
                        if node.humanoid_bone.is_finger():
                            node.pose = bone.transform.reverse_z()
                    else:
                        LOGGER.warn(f'{bone.name} not found')

        self._setup_model()
