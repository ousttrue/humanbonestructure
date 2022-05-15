from typing import Dict
import glm
from pydear.gizmo.gizmo import Gizmo, RayHit
from pydear.gizmo.gizmo_drag_handler import DragContext, GizmoDragHandler, Axis
from pydear.gizmo.shapes.shape import Shape
from pydear.scene.camera import Camera
from ..scene.node import Node
from ..humanoid.transform import Transform


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


class NodeDragHandler(GizmoDragHandler):
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
