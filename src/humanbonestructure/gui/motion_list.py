from typing import Iterable, List
import ctypes
from pydear import imgui as ImGui
from .selector import ItemList, Filter, Header
from ..formats.pose import Motion, Empty
from ..formats.humanoid_bones import HumanoidBone, HumanoidBodyParts


class PoseFilter(Filter[Motion]):
    def __init__(self) -> None:
        self.filter_has_trunk = (ctypes.c_bool * 1)(False)
        self.filter_has_legs = (ctypes.c_bool * 1)(False)
        self.filter_has_leftArm = (ctypes.c_bool * 1)(False)
        self.filter_has_leftFingers = (ctypes.c_bool * 1)(True)
        self.filter_has_rightArm = (ctypes.c_bool * 1)(False)
        self.filter_has_rightFingers = (ctypes.c_bool * 1)(False)
        self.filter_has_thumbnail0 = (ctypes.c_bool * 1)(True)
        super().__init__(self.filter)

    def filter(self, item: Motion):
        if self.filter_has_trunk[0] and not any(bone.get_part() == HumanoidBodyParts.Trunk for bone in item.get_humanbones()):
            return False
        if self.filter_has_legs[0] and not any(bone.get_part() == HumanoidBodyParts.Legs for bone in item.get_humanbones()):
            return False
        if self.filter_has_leftArm[0] and not any(bone.get_part() == HumanoidBodyParts.LeftArm for bone in item.get_humanbones()):
            return False
        if self.filter_has_leftFingers[0] and not any(bone.get_part() == HumanoidBodyParts.LeftFingers for bone in item.get_humanbones()):
            return False
        if self.filter_has_rightArm[0] and not any(bone.get_part() == HumanoidBodyParts.RightArm for bone in item.get_humanbones()):
            return False
        if self.filter_has_rightFingers[0] and not any(bone.get_part() == HumanoidBodyParts.RightFingers for bone in item.get_humanbones()):
            return False
        if self.filter_has_thumbnail0[0] and not any(bone == HumanoidBone.leftThumbProximal or bone == HumanoidBone.rightThumbProximal for bone in item.get_humanbones()):
            return False
        return True

    def show(self):
        chcked = False
        if ImGui.Checkbox("幹", self.filter_has_trunk):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("脚", self.filter_has_legs):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("左腕", self.filter_has_leftArm):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("左指", self.filter_has_leftFingers):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("右腕", self.filter_has_rightArm):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("右指", self.filter_has_rightFingers):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("has thumb0", self.filter_has_thumbnail0):
            chcked = True

        if chcked:
            self.fire()


class MotionList(ItemList[Motion]):
    def __init__(self) -> None:
        super().__init__()
        self.items.append(Empty())
        self._filter = PoseFilter()

        def on_filter_changed(_):
            self.apply()
        self._filter += on_filter_changed

        self.headers: List[Header] = [
            Header("name"),
            Header("幹", 15),
            Header("脚", 15),
            Header("左腕", 15),
            Header("左指", 15),
            Header("右腕", 15),
            Header("右指", 15),
        ]

    def filter(self, item: Motion) -> bool:
        if not item.get_humanbones():
            # empty
            return True
        if not self._filter.value:
            return True
        return self._filter.value(item)

    def columns(self, item: Motion) -> Iterable[str]:
        yield item.name
        yield 'O' if (HumanoidBodyParts.Trunk in item.get_humanboneparts()) else ''
        yield 'O' if (HumanoidBodyParts.Legs in item.get_humanboneparts()) else ''
        yield 'O' if (HumanoidBodyParts.LeftArm in item.get_humanboneparts()) else ''
        yield 'O' if (HumanoidBodyParts.LeftFingers in item.get_humanboneparts()) else ''
        yield 'O' if (HumanoidBodyParts.RightArm in item.get_humanboneparts()) else ''
        yield 'O' if (HumanoidBodyParts.RightFingers in item.get_humanboneparts()) else ''

    def start(self):
        # start OpenCV
        # app.loop.create_task(gui.video_capture.start_async())
        pass

    def stop(self):
        pass
