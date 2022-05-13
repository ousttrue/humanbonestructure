from typing import Optional, Dict
import logging
from OpenGL import GL
import glm
from pydear.scene.camera import Camera
from pydear.utils.mouse_event import MouseEvent
from pydear.utils.eventproperty import EventProperty
from pydear.gizmo.gizmo import Gizmo, RayHit
from pydear.gizmo.gizmo_event_handler import GizmoEventHandler
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


class DragContext:
    def __init__(self, x, y, manipulator, target: Shape, node_shape_map: Dict[Node, Shape]):
        self.y = y
        assert(manipulator)
        self.manipulator = manipulator
        self.manipulator.add_state(ShapeState.DRAG)
        assert target
        self.target = target

        self.node_shape_map = node_shape_map
        self.target_node = find_node(node_shape_map, target)
        self.init_quat = self.target_node.pose.rotation if self.target_node.pose else glm.quat()

    def drag(self, x: int, y: int):
        angle = (y - self.y) * 0.02
        if self.target:
            # parent = self.target_node.parent.world_matrix if self.target_node.parent else glm.mat4()
            r = self.init_quat * glm.angleAxis(angle, glm.vec3(0, 0, 1))
            self.target_node.pose = Transform.from_rotation(r)
            # apply
            parent = self.target_node.parent.world_matrix if self.target_node.parent else glm.mat4()
            self.target_node.calc_world_matrix(parent)
            for node, _ in self.target_node.traverse_node_and_parent():
                shape = self.node_shape_map.get(node)
                if shape:
                    shape.matrix.set(node.world_matrix *
                                     glm.mat4(node.local_axis))

    def end(self):
        self.manipulator.remove_state(ShapeState.DRAG)
        self.manipulator = None


class DragEventHandler(GizmoEventHandler):
    def __init__(self, gizmo: Gizmo, node_shape_map) -> None:
        super().__init__()
        self.selected = EventProperty[Optional[Shape]](None)

        # draggable
        from pydear.gizmo.shapes.ring_shape import RingShape
        self.ring = RingShape(inner=0.1, outer=0.2, depth=0.005,
                              color=glm.vec4(0.3, 0.3, 1, 1))
        gizmo.add_shape(self.ring)

        self.node_shape_map = node_shape_map
        self.context = None

    def drag_begin(self, hit: RayHit):
        if hit.shape == self.ring:
            # ring is not selectable
            self.context = DragContext(
                hit.x, hit.y, hit.shape, self.selected.value, self.node_shape_map)
        else:
            self.select(hit)

    def drag(self, x, y, dx, dy):
        if self.context:
            self.context.drag(x, y)

    def drag_end(self, x, y):
        if self.context:
            self.context.end()
            self.context = None

    def select(self, hit: RayHit):
        shape = hit.shape
        if shape != self.selected.value:
            # clear
            if self.selected.value:
                self.selected.value.remove_state(ShapeState.SELECT)
            # select
            self.selected.set(shape)
            if shape:
                shape.add_state(ShapeState.SELECT)
                self.ring.matrix.set(shape.matrix.value)
                self.ring.remove_state(ShapeState.HIDE)
            else:
                self.ring.add_state(ShapeState.HIDE)


class PoseScene:
    def __init__(self, mouse_event: MouseEvent) -> None:
        self.skeleton = None
        self.root: Optional[Node] = None
        self.selected: Optional[Node] = None
        #
        self.node_shape_map = {}
        self.gizmo = Gizmo()
        self.gizmo_handler = DragEventHandler(self.gizmo, self.node_shape_map)
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
            from .bone_shape import BoneShape
            for bone in HumanoidBone:
                if bone.is_enable():
                    node = self.root.find_humanoid_bone(bone)
                    if node:
                        shape = BoneShape.from_node(node)
                        self.gizmo.add_shape(shape)
                        self.node_shape_map[node] = shape

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
