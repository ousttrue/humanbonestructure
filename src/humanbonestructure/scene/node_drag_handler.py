from typing import Dict, Tuple, List, Type
import glm
from pydear.gizmo.gizmo import Gizmo, RayHit
from pydear.gizmo.gizmo_drag_handler import RingDragContext, RollDragContext, GizmoDragHandler, Axis
from pydear.gizmo.shapes.shape import Shape
from pydear.scene.camera import Camera, MouseInput
from ..formats.node import Node
from ..formats.transform import Transform
from ..humanoid.humanoid_bones import BoneBase


HAND_SCALE = glm.scale(glm.vec3(0.25, 0.25, 0.25))


def get_scale(selected: Shape, node_shape_map: Dict[Node, Shape]) -> glm.mat4:
    for node, shape in node_shape_map.items():
        if shape == selected:
            if node.humanoid_bone.base == BoneBase.hand or node.humanoid_bone.is_finger():
                return HAND_SCALE
    return glm.mat4()


def find_node(node_shape_map, target) -> Node:
    for node, shape in node_shape_map.items():
        if shape == target:
            return node
    raise RuntimeError()


def sync_gizmo_with_node(root, parent: glm.mat4, node_shape_map):
    root.calc_world_matrix(parent)
    for node, _ in root.traverse_node_and_parent():
        shape = node_shape_map.get(node)
        if shape:
            shape.matrix.set(node.world_matrix *
                             glm.mat4(node.local_axis))


class NodeRingDragContext(RingDragContext):
    def __init__(self, start_screen_pos: glm.vec2, *, manipulator: Shape, axis: Axis, camera: Camera, target: Shape,
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
        sync_gizmo_with_node(self.target_node, parent, self.node_shape_map)
        return world_matrix * get_scale(self.target, self.node_shape_map)


class NodeRollDragContext(RollDragContext):
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
        sync_gizmo_with_node(self.target_node, parent, self.node_shape_map)
        return world_matrix * get_scale(self.target, self.node_shape_map)


class NodeDragHandler(GizmoDragHandler):
    def __init__(self, gizmo: Gizmo, camera: Camera, node_shape_map: Dict[Node, Shape], on_drag_end) -> None:
        self.node_shape_map = node_shape_map
        super().__init__(gizmo, camera, inner=0.1, outer=0.2, depth=0.02)
        self.on_drag_end = on_drag_end

        def on_selected(selected: Shape):
            for k, v in self.drag_shapes.items():
                k.matrix.set(k.matrix.value *
                             get_scale(selected, node_shape_map))

        self.selected += on_selected

    def create_rotation_shapes(self, inner: float, outer: float, depth: float) -> Dict[Shape, Tuple[Type, dict]]:
        from pydear.gizmo.shapes.ring_shape import XRingShape, YRingShape, ZRingShape, XRollShape, YRollShape, ZRollShape
        return {
            XRingShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(1, 0.3, 0.3, 1)): (NodeRingDragContext, {'axis': Axis.X, 'node_shape_map': self.node_shape_map}),
            YRingShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(0.3, 1, 0.3, 1)): (NodeRingDragContext, {'axis': Axis.Y, 'node_shape_map': self.node_shape_map}),
            ZRingShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(0.3, 0.3, 1, 1)): (NodeRingDragContext, {'axis': Axis.Z, 'node_shape_map': self.node_shape_map}),
            XRollShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(1, 0.3, 0.3, 1)): (NodeRollDragContext, {'axis': Axis.X, 'node_shape_map': self.node_shape_map}),
            YRollShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(0.3, 1, 0.3, 1)): (NodeRollDragContext, {'axis': Axis.Y, 'node_shape_map': self.node_shape_map}),
            ZRollShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(0.3, 0.3, 1, 1)): (NodeRollDragContext, {'axis': Axis.Z, 'node_shape_map': self.node_shape_map}),
        }

    def drag(self, mouse_input: MouseInput, dx, dy):
        if self.context:
            m = self.context.drag(glm.vec2(mouse_input.x, mouse_input.y))
            for drag_shape in self.drag_shapes.keys():
                drag_shape.matrix.set(m)

    def end(self, mouse_input):
        super().end(mouse_input)
        self.on_drag_end()
