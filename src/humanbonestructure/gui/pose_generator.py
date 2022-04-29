from typing import Optional
from .bone_mask import BoneMask
from ..eventproperty import EventProperty
from ..formats.pose import Pose
from .motion_list import MotionList, Motion


class PoseGenerator:
    def __init__(self) -> None:
        self.bone_mask = BoneMask()
        self.motion_list = MotionList()
        self.pose_event = EventProperty(Pose('empty'))
        self.motion: Optional[Motion] = None

        def refilter():
            self.set_motion(self.motion)

        self.bone_mask.changed += refilter

    def show(self):
        self.motion_list._filter.show()
        self.bone_mask.show()

    def set_motion(self, motion: Optional[Motion]):
        self.motion = motion
        if motion:
            pose = motion.get_current_pose()
            self.set_pose(pose)
        else:
            self.set_pose(Pose('empty'))

    def set_pose(self, _pose: Pose):
        pose = Pose(_pose.name)
        pose.bones = [
            bone for bone in _pose.bones if bone.humanoid_bone and self.bone_mask.mask(bone.humanoid_bone)]
        self.pose_event.set(pose)
