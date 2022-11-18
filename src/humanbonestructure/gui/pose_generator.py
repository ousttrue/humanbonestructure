from typing import Optional
import ctypes
from .bone_mask import BoneMask
from ...scene.eventproperty import EventProperty
from ..humanoid.pose import Pose
from .motion_list import Motion
from pydear import imgui as ImGui


class PoseGenerator:
    def __init__(self) -> None:
        self.pose_event = EventProperty(Pose('empty'))
        self.motion: Optional[Motion] = None
        self.frame = (ctypes.c_int32*1)(0)

        # self.bone_mask = BoneMask()
        # def refilter():
        #     self.set_motion(self.motion)
        # self.bone_mask.changed += refilter

    def show(self, p_open):
        if self.motion:
            pose = self.motion.get_current_pose()
            self.set_pose(pose)
        else:
            self.set_pose(Pose('empty'))

        if not p_open[0]:
            return
        # self.motion_list._filter.show()
        if ImGui.Begin('motion', p_open):
            # self.bone_mask.show()
            if self.motion:
                ImGui.TextUnformatted(self.motion.name)
                ImGui.TextUnformatted(self.motion.get_info())
                for i, part in enumerate(self.motion.get_humanboneparts()):
                    if i:
                        ImGui.SameLine()
                    ImGui.TextUnformatted(part.name)

                end_frame = self.motion.get_frame_count()-1
                assert end_frame >= 0
                ImGui.SliderInt('frame', self.frame, 0, end_frame)
                self.motion.set_frame(self.frame[0])

        ImGui.End()

    def set_motion(self, motion: Optional[Motion]):
        self.motion = motion

    def set_pose(self, pose: Pose):
        # pose = Pose(_pose.name)
        # pose.bones = [
        #     bone for bone in _pose.bones if bone.humanoid_bone and self.bone_mask.mask(bone.humanoid_bone)]
        if pose == self.pose_event.value:
            return
        self.pose_event.set(pose)
