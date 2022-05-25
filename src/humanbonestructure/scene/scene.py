from typing import Optional, Tuple, Dict, List
import glm
from pydear.utils.mouse_event import MouseEvent, MouseInput
from pydear.utils.mouse_camera import MouseCamera
from pydear.gizmo.gizmo import Gizmo
from pydear.gizmo.gizmo_select_handler import GizmoSelectHandler
from pydear.gizmo.shapes.shape import Shape
from ..humanoid.pose import Pose
from ..humanoid.bone import Bone, Skeleton, Joint
from ..eventproperty import EventProperty
from ..humanoid.humanoid_bones import HumanoidBone
from ..builder.hierarchy import Hierarchy
from ..formats.transform import Transform
from .bone_drag_handler import BoneDragHandler
from .bone_shape import BoneShape


class Scene:
    def __init__(self, mouse_event: MouseEvent) -> None:
        self.skeleton: Optional[Skeleton] = None
        self.mouse_camera = MouseCamera(mouse_event, distance=4, y=-0.8)
        # gizmo
        self.gizmo = None
        self.bone_shape_map: Dict[Bone, Shape] = {}
        self.humanoid_joint_map: Dict[HumanoidBone, Joint] = {}
        # axis, delta
        self.bone_axis_map: Dict[HumanoidBone, glm.quat] = {}
        self.bone_delta_map: Dict[HumanoidBone, glm.quat] = {}
        self.hierarchy: Optional[Hierarchy] = None

    def render(self, mouse_input: MouseInput):
        camera = self.mouse_camera.camera
        camera.projection.resize(mouse_input.width, mouse_input.height)

        if self.gizmo:
            self.gizmo.process(camera, mouse_input.x, mouse_input.y)

        if self.hierarchy:
            self.hierarchy.render(camera)

    def update(self, skeleton: Optional[Skeleton], pose: Optional[Pose], hierarchy: Optional[Hierarchy],
               *,
               cancel_axis: bool = False, strict_delta: bool = False):
        self._update_skeleton(skeleton)
        self.hierarchy = hierarchy

        # assign pose to node hierarchy
        # if pose and pose.bones:
        if pose:
            if self.skeleton:
                self.skeleton.clear_pose()
                for humanoid_bone in HumanoidBone:
                    if not humanoid_bone.is_enable():
                        continue
                    joint = self.humanoid_joint_map.get(humanoid_bone)
                    if joint:
                        pose_rotation = pose.get_rotation(
                            humanoid_bone) if pose else glm.quat()
                        if cancel_axis and strict_delta:
                            a = self._get_cancel_axis(humanoid_bone)
                            d = self._get_strict_delta(humanoid_bone)
                            joint.pose = d * a * \
                                pose_rotation * glm.inverse(a)
                        elif cancel_axis:
                            a = self._get_cancel_axis(humanoid_bone)
                            joint.pose = a * \
                                pose_rotation * glm.inverse(a)
                        elif strict_delta:
                            d = self._get_strict_delta(humanoid_bone)
                            joint.pose = d * pose_rotation
                        else:
                            joint.pose = pose_rotation
                    else:
                        pass
                        # raise RuntimeError()

                self.sync_gizmo()

            if self.hierarchy:
                # for pose_bone in pose.bones:
                #     self.hierarchy[pose_bone.humanoid_bone].pose = pose_bone.transform
                for humanoid_bone in HumanoidBone:
                    if not humanoid_bone.is_enable():
                        continue
                    joint = self.humanoid_joint_map.get(humanoid_bone)
                    if joint:
                        self.hierarchy[humanoid_bone].pose = Transform.from_rotation(
                            joint.pose)

                self.hierarchy.root.calc_world_matrix(glm.mat4())

    def _get_cancel_axis(self, humanoid_bone: HumanoidBone) -> glm.quat:
        return self.bone_axis_map.get(humanoid_bone, glm.quat())

    def _get_strict_delta(self, humanoid_bone: HumanoidBone) -> glm.quat:
        return self.bone_delta_map.get(humanoid_bone, glm.quat())

    def _update_skeleton(self, skeleton: Optional[Skeleton]):
        if self.skeleton == skeleton:
            return
        self.skeleton = skeleton
        if not self.skeleton:
            return

        # get axis
        self.bone_axis_map.clear()
        self.skeleton.cancel_axis()
        for bone in self.skeleton.enumerate():
            self.bone_axis_map[bone.head.humanoid_bone] = bone.local_axis

        # get delta
        self.bone_delta_map.clear()
        self.skeleton.strict_tpose()
        for bone in self.skeleton.enumerate():
            self.bone_delta_map[bone.head.humanoid_bone] = bone.head.pose

        self.skeleton.clear_axis()
        self.skeleton.clear_pose()

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
                    self.mouse_camera.view.set_gaze(position)
            self.drag_handler.selected += on_selected
        else:
            def raise_pose():
                assert self.skeleton
                pose = self.skeleton.to_pose()
                self.pose_changed.set(pose)

            camera = self.mouse_camera.camera
            self.drag_handler = BoneDragHandler(
                self.gizmo, camera, self.joint_shape_map, raise_pose)
            self.mouse_camera.mouse_event.bind_left_drag(self.drag_handler)
            self.pose_changed = EventProperty[Pose](Pose('empty'))

            def on_selected(selected: Optional[Shape]):
                if selected:
                    position = selected.matrix.value[3].xyz
                    camera.view.set_gaze(position)
            self.drag_handler.selected += on_selected

    def sync_gizmo(self):
        if not self.skeleton:
            return

        self.skeleton.calc_world_matrix()
        for bone, shape in self.bone_shape_map.items():
            shape.matrix.set(bone.head.world.get_matrix()
                             * glm.mat4(bone.local_axis))

    def clear_pose(self):
        if not self.skeleton:
            return
        self.skeleton.clear_pose()
        self.sync_gizmo()
