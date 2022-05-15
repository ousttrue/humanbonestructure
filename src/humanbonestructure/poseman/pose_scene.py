from typing import Optional
import pathlib
import logging
from OpenGL import GL
import glm
from pydear.scene.camera import Camera
from pydear.utils.mouse_event import MouseEvent
from pydear.utils.nanovg_renderer import NanoVgRenderer, nvg_line_from_to
from pydear.gizmo.gizmo import Gizmo
from ..humanoid.humanoid_skeleton import HumanoidSkeleton
from ..scene.node import Node

LOGGER = logging.getLogger(__name__)
RED = glm.vec4(1, 0, 0, 1)
GREEN = glm.vec4(0, 1, 0, 1)
BLUE = glm.vec4(0, 0, 1, 1)
SELECTED_COLOR = glm.vec3(0.5, 0.5, 1)


class PoseScene:
    def __init__(self, mouse_event: MouseEvent, camera: Camera, font: pathlib.Path) -> None:
        self.skeleton = None
        self.root: Optional[Node] = None
        self.selected: Optional[Node] = None
        #
        self.node_shape_map = {}
        self.gizmo = Gizmo()
        from .node_drag_handler import NodeDragHandler
        self.drag_handler = NodeDragHandler(
            self.gizmo, camera, self.node_shape_map)
        self.drag_handler.bind_mouse_event_with_gizmo(mouse_event, self.gizmo)

        self.nvg = NanoVgRenderer(font)

    def set_skeleton(self, skeleton: Optional[HumanoidSkeleton]):
        self.skeleton = skeleton
        if self.skeleton:
            # setup node
            self.root = self.skeleton.to_node()
            self.root.init_human_bones()
            for bone, _ in self.root.traverse_node_and_parent():
                if bone.humanoid_bone.is_enable():
                    bone.local_axis = glm.quat(
                        bone.humanoid_bone.get_classification().get_local_axis())
            self.root.calc_world_matrix(glm.mat4())

            # setup gizmo
            from ..gui.bone_shape import BoneShape
            for k, v in BoneShape.from_root(self.root, self.gizmo).items():
                self.node_shape_map[k] = v

        else:
            self.root = None

    def get_root(self) -> Optional[Node]:
        return self.root

    def get_selected(self) -> Optional[Node]:
        return self.selected

    def set_selected(self, selected: Optional[Node]):
        self.selected = selected

    def show_option(self):
        pass

    def render(self, camera: Camera, x: int, y: int):
        GL.glEnable(GL.GL_DEPTH_TEST)
        if not self.root:
            return

        self.gizmo.process(camera, x, y)

        context = self.drag_handler.context
        if context:
            start = context.start_screen_pos
            with self.nvg.render(camera.projection.width, camera.projection.height) as vg:
                nvg_line_from_to(vg, start.x, start.y, x, y)
                if not context.edge:
                    a = context.left
                    b = context.right
                    nvg_line_from_to(vg, a.x, a.y, b.x, b.y)
