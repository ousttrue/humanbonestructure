from typing import Optional, Any, List
import logging
import ctypes
from pydear import imgui as ImGui
from ..formats.vpd_loader import Vpd, HumanoidBone

LOGGER = logging.getLogger(__name__)


class Selector:
    def __init__(self, on_selected) -> None:
        self.items: List[Vpd] = []
        self.filtered_items: List[Vpd] = []
        self.selected: Optional[Any] = None
        self.on_selected = on_selected

        self.filter_has_lefthand = (ctypes.c_bool * 1)(True)
        self.filter_has_thumbnail0 = (ctypes.c_bool * 1)(True)

    def apply(self):
        self.filtered_items.clear()
        for item in self.items:
            if self.filter_has_lefthand[0] and not any(bone.humanoid_bone.value.startswith('left') for bone in item.bones if bone.humanoid_bone):
                continue
            if self.filter_has_thumbnail0[0] and not any(bone.humanoid_bone == HumanoidBone.leftThumbProximal or bone.humanoid_bone == HumanoidBone.rightThumbProximal for bone in item.bones if bone.humanoid_bone):
                continue
            self.filtered_items.append(item)

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin("select vpd", p_open):
            if ImGui.Checkbox("leftHand", self.filter_has_lefthand):
                self.apply()
            if ImGui.Checkbox("has thumb0", self.filter_has_thumbnail0):
                self.apply()

            selected = None
            for item in self.filtered_items:
                current = ImGui.Selectable(
                    str(item), item == self.selected)
                if current:
                    selected = item
            if selected:
                self.selected = selected
                self.on_selected(selected)
        ImGui.End()
