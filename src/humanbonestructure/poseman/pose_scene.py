from typing import Optional, Dict
from enum import Enum, auto
import logging
from OpenGL import GL
import glm
from pydear.scene.camera import Camera
from pydear.utils.mouse_event import MouseEvent
from pydear.utils.eventproperty import EventProperty
from pydear.gizmo.gizmo import Gizmo, RayHit
from pydear.gizmo.gizmo_event_handler import GizmoEventHandler
from pydear.gizmo.gizmo_drag_handler import GizmoDragHandler, DragContext, Axis
from pydear.gizmo.shapes.shape import Shape, ShapeState
from ..humanoid.humanoid_skeleton import HumanoidSkeleton, Fingers, HumanoidBone
from ..humanoid.transform import Transform
from ..scene.node import Node

LOGGER = logging.getLogger(__name__)
RED = glm.vec4(1, 0, 0, 1)
GREEN = glm.vec4(0, 1, 0, 1)
BLUE = glm.vec4(0, 0, 1, 1)
SELECTED_COLOR = glm.vec3(0.5, 0.5, 1)


def find_node(node_shape_map, target) -> Node:
    for node, shape in node_shape_map.items():
        if shape == target:
            return node
    raise RuntimeError()


class NodeDragContext(DragContext):
    def __init__(self, start_screen_pos: glm.vec2, *, manipulator, axis: Axis, camera: Camera, target: Shape,
                 node_shape_map: Dict[Node, Shape]):
        super().__init__(start_screen_pos, manipulator=manipulator,
                         axis=axis, target=target, camera=camera)
        self.node_shape_map = node_shape_map
        self.target_node = find_node(node_shape_map, target)

    def drag(self, cursor_pos: glm.vec2) -> glm.mat4:
        world_matrix = super().drag(cursor_pos)
        local_axis = self.target_node.local_axis
        parent = self.target_node.parent.world_matrix if self.target_node.parent else glm.mat4()
        local_matrix = glm.inverse(parent) * world_matrix
        self.target_node.pose = Transform.from_rotation(glm.normalize(
            glm.quat(local_matrix) * glm.inverse(local_axis)))
        self.target_node.calc_world_matrix(parent)
        for node, _ in self.target_node.traverse_node_and_parent():
            shape = self.node_shape_map.get(node)
            if shape:
                shape.matrix.set(node.world_matrix *
                                 glm.mat4(node.local_axis))
        return world_matrix


class NodeDragEventHandler(GizmoDragHandler):
    def __init__(self, gizmo: Gizmo, camera: Camera, node_shape_map) -> None:
        super().__init__(gizmo, camera, inner=0.1, outer=0.2, depth=0.005)
        self.node_shape_map = node_shape_map

    def drag_begin(self, hit: RayHit):
        match hit.shape:
            case self.x_ring:
                # ring is not selectable
                self.context = NodeDragContext(
                    hit.cursor_pos, manipulator=hit.shape, axis=Axis.X,
                    camera=self.camera,
                    target=self.selected.value,
                    node_shape_map=self.node_shape_map)
            case self.y_ring:
                # ring is not selectable
                self.context = NodeDragContext(
                    hit.cursor_pos, manipulator=hit.shape, axis=Axis.Y,
                    camera=self.camera,
                    target=self.selected.value,
                    node_shape_map=self.node_shape_map)
            case self.z_ring:
                # ring is not selectable
                self.context = NodeDragContext(
                    hit.cursor_pos,
                    manipulator=hit.shape, axis=Axis.Z,
                    camera=self.camera,
                    target=self.selected.value,
                    node_shape_map=self.node_shape_map)
            case _:
                self.select(hit)


class PoseScene:
    def __init__(self, mouse_event: MouseEvent, camera: Camera) -> None:
        self.skeleton = None
        self.root: Optional[Node] = None
        self.selected: Optional[Node] = None
        #
        self.node_shape_map = {}
        self.gizmo = Gizmo()
        self.gizmo_handler = NodeDragEventHandler(
            self.gizmo, camera, self.node_shape_map)
        self.gizmo_handler.bind_mouse_event_with_gizmo(mouse_event, self.gizmo)

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
