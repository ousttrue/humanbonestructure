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
from ..humanoid import blender_coordinate
from ..scene.node import Node
from ..scene.node_drag_handler import NodeDragHandler, sync_gizmo_with_node

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
        self.drag_handler = NodeDragHandler(
            self.gizmo, self.camera, self.node_shape_map, self.on_drag_end)
        self.drag_handler.bind_mouse_event_with_gizmo(
            self.mouse_event, self.gizmo)

        # camera gaze when selected
        def on_selected(selected: Optional[Shape]):
            if selected:
                position = selected.matrix.value[3].xyz
                self.camera.view.set_gaze(position)
                for node, shape in self.node_shape_map.items():
                    if shape == selected:
                        self.set_selected(node)
                        break
        self.drag_handler.selected += on_selected

        self.nvg = NanoVgRenderer(font)

        self.pose_changed = EventProperty[Pose](Pose('empty'))

    def on_drag_end(self):
        assert self.root
        pose = self.root.to_pose()
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
                        blender_coordinate.BONE_COORDS_MAP[bone.humanoid_bone])
            self.root.calc_world_matrix(glm.mat4())

            # setup gizmo
            from ..gui.bone_shape import BoneShape
            for k, v in BoneShape.from_root(self.root, self.gizmo).items():
                self.node_shape_map[k] = v

        else:
            self.root = None

    def clear_pose(self):
        if not self.root:
            return
        self.root.clear_pose()
        sync_gizmo_with_node(self.root, glm.mat4(),
                             self.drag_handler.node_shape_map)
        self.drag_handler.select(None)
        self.pose_changed.set(self.root.to_pose())

    def get_root(self) -> Optional[Node]:
        return self.root

    def get_selected(self) -> Optional[Node]:
        return self.selected

    def set_selected(self, selected: Optional[Node]):
        self.selected = selected

        if selected:
            # select from ImGui list
            shape = self.node_shape_map.get(selected)
            if shape and self.drag_handler.selected.value != shape:
                self.drag_handler.select(shape)
                self.camera.middle_drag.reset()

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
            with self.nvg.render(self.camera.projection.width, self.camera.projection.height) as vg:
                context.nvg_draw(vg)
