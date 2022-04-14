from typing import Optional, Any, List
import ctypes
from pydear import imgui as ImGui
from ..formats.vpd_loader import Vpd, HumanoidBone


class Selector:
    def __init__(self, on_selected) -> None:
        self.items: List[Vpd] = []
        self.selected: Optional[Any] = None
        self.on_selected = on_selected

        self.filter_has_lefthand = (ctypes.c_bool * 1)(True)
        self.filter_has_thumbnail0 = (ctypes.c_bool * 1)(True)

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin("select vpd", p_open):
            ImGui.Checkbox("leftHand", self.filter_has_lefthand)
            ImGui.Checkbox("has thumb0", self.filter_has_thumbnail0)

            selected = None
            for item in self.items:
                if self.filter_has_lefthand[0] and not any(bone.humanoid_bone.value.startswith('left') for bone in item.bones if bone.humanoid_bone):
                    continue
                if self.filter_has_thumbnail0[0] and not any(bone.humanoid_bone == HumanoidBone.leftThumbProximal or bone.humanoid_bone == HumanoidBone.rightThumbProximal for bone in item.bones if bone.humanoid_bone):
                    continue

                current = ImGui.Selectable(
                    str(item), item == self.selected)
                if current:
                    selected = item
            if selected:
                self.selected = selected
                self.on_selected(selected)
        ImGui.End()
