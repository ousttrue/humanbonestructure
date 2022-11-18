from typing import Dict, Tuple, Type
import glm
from pydear.gizmo.gizmo_drag_handler import RingDragContext, RollDragContext, GizmoDragHandler, Axis
from pydear.gizmo.gizmo import Gizmo
from pydear.gizmo.shapes.shape import Shape
from pydear.scene.camera import Camera, MouseInput
from ..humanoid.humanoid_bones import BoneBase
from ..humanoid.bone import Joint, TR

HAND_SCALE = glm.scale(glm.vec3(0.25, 0.25, 0.25))


def get_scale(selected: Shape, joint_shape_map: Dict[Joint, Shape]) -> glm.mat4:
    for joint, shape in joint_shape_map.items():
        if shape == selected:
            if joint.humanoid_bone.base == BoneBase.hand or joint.humanoid_bone.is_finger():
                return HAND_SCALE
    return glm.mat4()


def find_joint(joint_shape_map, target) -> Joint:
    for joint, shape in joint_shape_map.items():
        if shape == target:
            return joint
    raise RuntimeError()


def sync_gizmo_with_joint(root: Joint, parent: glm.mat4, joint_shape_map: Dict[Joint, Shape]):
    root.calc_world(TR.from_matrix(parent))
    for joint in root.traverse():
        shape = joint_shape_map.get(joint)
        if shape:
            shape.matrix.set(joint.world.get_matrix() *
                             glm.mat4(joint.local_axis))


class JointRingDragContext(RingDragContext):
    def __init__(self, start_screen_pos: glm.vec2, *, manipulator: Shape, axis: Axis, camera: Camera, target: Shape,
                 joint_shape_map: Dict[Joint, Shape]):
        super().__init__(start_screen_pos, manipulator=manipulator,
                         axis=axis, target=target, camera=camera)

        self.joint_shape_map = joint_shape_map
        self.target_joint = find_joint(joint_shape_map, target)

    def drag(self, cursor_pos: glm.vec2) -> glm.mat4:
        world_matrix = super().drag(cursor_pos)
        local_axis = self.target_joint.local_axis
        parent = self.target_joint.get_parent_world_matrix()
        local_matrix = glm.inverse(parent) * world_matrix
        self.target_joint.pose = glm.normalize(
            glm.quat(local_matrix) * glm.inverse(local_axis))
        sync_gizmo_with_joint(self.target_joint, parent, self.joint_shape_map)
        return world_matrix * get_scale(self.target, self.joint_shape_map)


class JointRollDragContext(RollDragContext):
    def __init__(self, start_screen_pos: glm.vec2, *, manipulator, axis: Axis, camera: Camera, target: Shape,
                 joint_shape_map: Dict[Joint, Shape]):
        super().__init__(start_screen_pos, manipulator=manipulator,
                         axis=axis, target=target, camera=camera)
        self.joint_shape_map = joint_shape_map
        self.target_joint = find_joint(joint_shape_map, target)

    def drag(self, cursor_pos: glm.vec2) -> glm.mat4:
        world_matrix = super().drag(cursor_pos)
        local_axis = self.target_joint.local_axis
        parent = self.target_joint.get_parent_world_matrix()
        local_matrix = glm.inverse(parent) * world_matrix
        self.target_joint.pose = glm.normalize(
            glm.quat(local_matrix) * glm.inverse(local_axis))
        sync_gizmo_with_joint(self.target_joint, parent, self.joint_shape_map)
        return world_matrix * get_scale(self.target, self.joint_shape_map)


class BoneDragHandler(GizmoDragHandler):
    def __init__(self, gizmo: Gizmo, camera: Camera, joint_shape_map: Dict[Joint, Shape], on_drag_end) -> None:
        self.joint_shape_map = joint_shape_map
        super().__init__(gizmo, camera, inner=0.1, outer=0.2, depth=0.02)
        self.on_drag_end = on_drag_end

        def on_selected(selected: Shape):
            for k, v in self.drag_shapes.items():
                k.matrix.set(k.matrix.value *
                             get_scale(selected, joint_shape_map))

        self.selected += on_selected

    def create_rotation_shapes(self, inner: float, outer: float, depth: float) -> Dict[Shape, Tuple[Type, dict]]:
        from pydear.gizmo.shapes.ring_shape import XRingShape, YRingShape, ZRingShape, XRollShape, YRollShape, ZRollShape
        return {
            XRingShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(1, 0.3, 0.3, 1)): (JointRingDragContext, {'axis': Axis.X, 'joint_shape_map': self.joint_shape_map}),
            YRingShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(0.3, 1, 0.3, 1)): (JointRingDragContext, {'axis': Axis.Y, 'joint_shape_map': self.joint_shape_map}),
            ZRingShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(0.3, 0.3, 1, 1)): (JointRingDragContext, {'axis': Axis.Z, 'joint_shape_map': self.joint_shape_map}),
            XRollShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(1, 0.3, 0.3, 1)): (JointRollDragContext, {'axis': Axis.X, 'joint_shape_map': self.joint_shape_map}),
            YRollShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(0.3, 1, 0.3, 1)): (JointRollDragContext, {'axis': Axis.Y, 'joint_shape_map': self.joint_shape_map}),
            ZRollShape(inner=inner, outer=outer, depth=depth, color=glm.vec4(0.3, 0.3, 1, 1)): (JointRollDragContext, {'axis': Axis.Z, 'joint_shape_map': self.joint_shape_map}),
        }

    def drag(self, mouse_input: MouseInput, dx, dy):
        if self.context:
            m = self.context.drag(glm.vec2(mouse_input.x, mouse_input.y))
            for drag_shape in self.drag_shapes.keys():
                drag_shape.matrix.set(m)

    def end(self, mouse_input):
        super().end(mouse_input)
        self.on_drag_end()
