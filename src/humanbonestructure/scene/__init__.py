from typing import Optional, List
import ctypes
import pathlib
import logging
from OpenGL import GL
import glm
from pydear import imgui as ImGui
from pydear.scene.camera import Camera
from ..formats import pmd_loader, gltf_loader, vpd_loader, pmx_loader, bytesreader
from .node import Node
from .mesh_renderer import MeshRenderer
from ..formats.buffer_types import Float2, Float3, Float4, Vertex4BoneWeights
from ..formats.humanoid_bones import HumanoidBone
from .axis import Axis
from ..formats.transform import Transform
LOGGER = logging.getLogger(__name__)


class Scene:
    def __init__(self) -> None:
        # gizmo
        self.axis = Axis()
        # scene
        self.nodes: List[Node] = []
        self.roots: List[Node] = []
        # gui
        self.camera = Camera(distance=4, y=-0.8)
        self.hover = False

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
        self.nodes.clear()
        self.roots.clear()

        pmd = pmd_loader.Pmd(path.read_bytes())
        LOGGER.debug(pmd)

        from .builder import pmd_builder
        pmd_builder.build(self, pmd)

        # finalize
        for root in self.roots:
            root.initialize()
            root.calc_skinning(glm.mat4())

    def load_pmx(self, path: pathlib.Path):
        self.nodes.clear()
        self.roots.clear()

        pmx = pmx_loader.Pmx(path.read_bytes())
        LOGGER.debug(pmx)

        from .builder import pmx_builder
        pmx_builder.build(self, pmx)

        # finalize
        for root in self.roots:
            root.initialize()
            root.calc_skinning(glm.mat4())

    def load_glb(self, path: pathlib.Path):
        self.nodes.clear()
        self.roots.clear()

        gltf = gltf_loader.Gltf.load_glb(path.read_bytes())
        LOGGER.debug(gltf)

        from .builder import gltf_builder
        gltf_builder.build(self, gltf)

        # finalize
        for root in self.roots:
            root.initialize()
            root.calc_skinning(glm.mat4())

    def create_model(self):
        from .builder import create
        create.create_scene(self)

        # finalize
        for root in self.roots:
            root.initialize()
            root.calc_skinning(glm.mat4())

    def render(self, w: int, h: int):
        # camera update
        self.camera.onResize(w, h)
        if self.hover:
            wx, wy = ImGui.GetWindowPos()
            wy += ImGui.GetFrameHeight()
            io = ImGui.GetIO()

            x = int(io.MousePos.x-wx)
            y = int(io.MousePos.y-wy)

            if io.MouseDown[0]:
                self.camera.onLeftDown(x, y)
            else:
                self.camera.onLeftUp(x, y)

            if io.MouseDown[1]:
                self.camera.onRightDown(x, y)
            else:
                self.camera.onRightUp(x, y)

            if io.MouseDown[2]:
                self.camera.onMiddleDown(x, y)
            else:
                self.camera.onMiddleUp(x, y)

            self.camera.onMotion(x, y)
            self.camera.onWheel(int(-io.MouseWheel))

        # render
        for root in self.roots:
            self.render_node(root)

        self.axis.render(self.camera)

    def render_node(self, node: Node):
        if node.renderer:
            node.renderer.render(self.camera, node)

        from . import local_axis
        if not node.gizmo:
            node.gizmo = local_axis.create_local_axis(self.camera, node)
        GL.glEnable(GL.GL_DEPTH_TEST)
        node.gizmo.draw()

        for child in node.children:
            self.render_node(child)

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

        # calc skinning matrix
        for root in self.roots:
            root.calc_skinning(glm.mat4())
