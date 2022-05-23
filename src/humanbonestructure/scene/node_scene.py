from typing import Optional, Tuple, Dict
import glm
from pydear.utils.mouse_event import MouseEvent
from pydear.scene.camera import Camera, ArcBall, ScreenShift
from pydear.gizmo.gizmo import Gizmo
from pydear.gizmo.gizmo_select_handler import GizmoSelectHandler
from .bone_drag_handler import BoneDragHandler
from pydear.gizmo.shapes.shape import Shape
from ..humanoid.pose import Pose
from ..humanoid.bone import Bone, Skeleton, Joint
from ..eventproperty import EventProperty
from ..humanoid.humanoid_bones import HumanoidBone
from .unitychan_coords import get_unitychan_coords
from .node import Node
from .bone_shape import BoneShape


class NodeScene:
    def __init__(self, mouse_event: MouseEvent) -> None:
        self.skeleton: Optional[Skeleton] = None

        self.mouse_event = mouse_event
        self.camera = Camera(distance=4, y=-0.8)
        self.arc = ArcBall(self.camera.view, self.camera.projection)
        self.mouse_event.bind_right_drag(self.arc)
        self.shift = ScreenShift(self.camera.view, self.camera.projection)
        self.mouse_event.bind_middle_drag(self.shift)
        self.mouse_event.wheel += [self.shift.wheel]

        self.gizmo = None
        self.bone_shape_map: Dict[Bone, Shape] = {}
        self.cancel_axis = False

        self.humanoid_joint_map: Dict[HumanoidBone, Joint] = {}

    def render(self, w: int, h: int):
        if not self.gizmo:
            return
        mouse_input = self.mouse_event.last_input
        assert(mouse_input)
        self.camera.projection.resize(w, h)
        self.gizmo.process(self.camera, mouse_input.x, mouse_input.y)

    def update(self, skeleton: Optional[Skeleton], pose: Optional[Pose], cancel_axis: bool = False, strict_delta: bool = False):
        self._update_skeleton(skeleton)
        if not self.skeleton:
            return

        # assign pose to node hierarchy
        if pose and pose.bones:
            self.skeleton.clear_pose()
            for bone in pose.bones:
                if bone.humanoid_bone:
                    joint = self.humanoid_joint_map.get(bone.humanoid_bone)
                    if joint:
                        if cancel_axis and strict_delta:
                            a = self._get_cancel_axis(bone.humanoid_bone)
                            d = self._get_strict_delta(bone.humanoid_bone)
                            joint.pose = d * a * \
                                bone.transform.rotation * glm.inverse(a)
                        elif cancel_axis:
                            a = self._get_cancel_axis(bone.humanoid_bone)
                            d = self._get_strict_delta(bone.humanoid_bone)
                            joint.pose = a * \
                                bone.transform.rotation * glm.inverse(a)
                        elif strict_delta:
                            d = self._get_strict_delta(bone.humanoid_bone)
                            joint.pose = d * bone.transform.rotation
                        else:
                            joint.pose = bone.transform.rotation
                    else:
                        pass
                        # raise RuntimeError()
                else:
                    raise RuntimeError()

        self.sync_gizmo()

    def _get_cancel_axis(self, humanoid_bone: HumanoidBone) -> glm.quat:
        return glm.quat()

    def _get_strict_delta(self, humanoid_bone: HumanoidBone) -> glm.quat:
        return glm.quat()

    def _update_skeleton(self, skeleton):
        if self.skeleton == skeleton:
            return
        self.skeleton = skeleton
        if not self.skeleton:
            return
        self.gizmo = Gizmo()
        self.bone_shape_map = BoneShape.from_skeleton(
            self.skeleton, self.gizmo)
        self.joint_shape_map = {
            bone.head: shape for bone, shape in self.bone_shape_map.items()}
        self.humanoid_joint_map = {
            bone.head.humanoid_bone: bone.head for bone, shape in self.bone_shape_map.items()}

        # shape select
        if False:
            self.drag_handler = GizmoSelectHandler(self.gizmo)
            self.mouse_event.bind_left_drag(self.drag_handler)

            def on_selected(selected: Optional[Shape]):
                if selected:
                    position = selected.matrix.value[3].xyz
                    self.camera.view.set_gaze(position)
            self.drag_handler.selected += on_selected
        else:
            def raise_pose():
                assert self.skeleton
                pose = self.skeleton.to_pose()
                self.pose_changed.set(pose)

            self.drag_handler = BoneDragHandler(
                self.gizmo, self.camera, self.joint_shape_map, raise_pose)
            self.mouse_event.bind_left_drag(self.drag_handler)
            self.pose_changed = EventProperty[Pose](Pose('empty'))

            def on_selected(selected: Optional[Shape]):
                if selected:
                    position = selected.matrix.value[3].xyz
                    self.camera.view.set_gaze(position)
            self.drag_handler.selected += on_selected

    def sync_gizmo(self):
        if not self.skeleton:
            return

        self.skeleton.calc_world_matrix()
        for bone, shape in self.bone_shape_map.items():
            shape.matrix.set(bone.head.world.get_matrix()
                             * glm.mat4(bone.local_axis))
