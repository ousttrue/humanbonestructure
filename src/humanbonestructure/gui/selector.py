from typing import Optional, Any, List
import logging
import ctypes
from pydear import imgui as ImGui
from ..formats.vpd_loader import Vpd, HumanoidBone

LOGGER = logging.getLogger(__name__)


class Selector:
    def __init__(self, name: str, on_selected) -> None:
        self.name = name
        self.items: List[Vpd] = []
        self.filtered_items: List[Vpd] = []
        self.selected: Optional[Any] = None
        self.on_selected = on_selected

        self.filter_has_lefthand = (ctypes.c_bool * 1)(True)
        self.filter_has_thumbnail0 = (ctypes.c_bool * 1)(True)

        self.use_except_finger = (ctypes.c_bool * 1)(False)
        self.use_finger = (ctypes.c_bool * 1)(True)
        self.mask = lambda x: True

    def apply(self):
        self.filtered_items.clear()
        for item in self.items:
            if item.bones:
                if self.filter_has_lefthand[0] and not any(bone.humanoid_bone.value.startswith('left') for bone in item.bones if bone.humanoid_bone):
                    continue
                if self.filter_has_thumbnail0[0] and not any(bone.humanoid_bone == HumanoidBone.leftThumbProximal or bone.humanoid_bone == HumanoidBone.rightThumbProximal for bone in item.bones if bone.humanoid_bone):
                    continue
            self.filtered_items.append(item)

        if self.use_except_finger[0] and self.use_finger[0]:
            self.mask = lambda x: True
        elif self.use_except_finger[0]:
            self.mask = lambda x: not x.is_finger()
        elif self.use_finger[0]:
            self.mask = lambda x: x.is_finger()
        else:
            self.mask = lambda x: False

        if self.selected:
            self.on_selected(self.selected, self.mask)

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin(self.name, p_open):
            if ImGui.Checkbox("leftHand", self.filter_has_lefthand):
                self.apply()
            ImGui.SameLine()
            if ImGui.Checkbox("has thumb0", self.filter_has_thumbnail0):
                self.apply()

            if ImGui.Checkbox("mask except finger", self.use_except_finger):
                self.apply()
            ImGui.SameLine()
            if ImGui.Checkbox("mask finger", self.use_finger):
                self.apply()

            selected = None
            for item in self.filtered_items:
                current = ImGui.Selectable(
                    str(item), item == self.selected)
                if current:
                    selected = item
            if selected:
                self.selected = selected
                self.on_selected(selected, self.mask)
        ImGui.End()
