from typing import Optional, Dict
import pathlib
import logging
import glm
from pydear.scene.camera import Camera
from pydear.utils.mouse_event import MouseEvent
from pydear.utils.nanovg_renderer import NanoVgRenderer, nvg_line_from_to
from pydear.utils.eventproperty import EventProperty
from pydear.gizmo.gizmo import Gizmo
from pydear.gizmo.shapes.shape import Shape
from ..humanoid.humanoid_skeleton import HumanoidSkeleton
from ..humanoid.pose import Pose, BonePose
from ..scene.node import Node

LOGGER = logging.getLogger(__name__)
RED = glm.vec4(1, 0, 0, 1)
GREEN = glm.vec4(0, 1, 0, 1)
BLUE = glm.vec4(0, 0, 1, 1)
SELECTED_COLOR = glm.vec3(0.5, 0.5, 1)


class PoseScene:
    def __init__(self, mouse_event: MouseEvent, font: pathlib.Path) -> None:
        self.camera = Camera(distance=6, y=-0.8)
        self.mouse_event = mouse_event
        self.camera.bind_mouse_event(self.mouse_event)

        self.skeleton: Optional[HumanoidSkeleton] = None
        self.root: Optional[Node] = None
        self.selected: Optional[Node] = None
        #
        self.node_shape_map: Dict[Node, Shape] = {}
        self.gizmo = Gizmo()
        from .node_drag_handler import NodeDragHandler
        self.drag_handler = NodeDragHandler(
            self.gizmo, self.camera, self.node_shape_map, self.on_drag_end)
        self.drag_handler.bind_mouse_event_with_gizmo(
            self.mouse_event, self.gizmo)

        self.nvg = NanoVgRenderer(font)

        self.pose_changed = EventProperty[Pose](Pose('empty'))

    def on_drag_end(self):
        assert self.root
        pose = Pose('pose')
        for node, _ in self.root.traverse_node_and_parent(only_human_bone=True):
            if node.pose:
                pose.bones.append(
                    BonePose(node.name, node.humanoid_bone, node.pose))
        self.pose_changed.set(pose)

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

    def render(self, w: int, h: int):
        self.camera.projection.resize(w, h)
        mouse_input = self.mouse_event.last_input
        if not mouse_input:
            return

        if not self.root:
            return

        self.gizmo.process(self.camera, mouse_input.x, mouse_input.y)

        context = self.drag_handler.context
        if context:
            start = context.start_screen_pos
            with self.nvg.render(self.camera.projection.width, self.camera.projection.height) as vg:
                nvg_line_from_to(vg, start.x, start.y,
                                 mouse_input.x, mouse_input.y)
                if not context.edge:
                    a = context.left
                    b = context.right
                    nvg_line_from_to(vg, a.x, a.y, b.x, b.y)
