import ctypes
from pydear import imgui as ImGui
from ..formats.humanoid_bones import HumanoidBone


class VpdMask:
    def __init__(self) -> None:
        self.use_except_finger = (ctypes.c_bool * 1)(False)
        self.use_finger = (ctypes.c_bool * 1)(True)
        self.pred = lambda x: True

    def show(self):
        ImGui.Checkbox("except finger", self.use_except_finger)
        ImGui.SameLine()
        ImGui.Checkbox("finger", self.use_finger)
        if self.use_except_finger[0] and self.use_finger[0]:
            self.pred = (lambda x: True)
        elif self.use_except_finger[0]:
            self.pred = (lambda x: not x.is_finger())
        elif self.use_finger[0]:
            self.pred = (lambda x: x.is_finger())
        else:
            self.pred = (lambda x: False)

    def mask(self, bone: HumanoidBone) -> bool:
        return self.pred(bone)
