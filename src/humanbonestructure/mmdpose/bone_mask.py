import ctypes
from pydear import imgui as ImGui
from ..formats.humanoid_bones import HumanoidBone
from ..eventproperty import Event
import logging
LOGGER = logging.getLogger(__name__)


class BoneMask:
    def __init__(self) -> None:
        self.use_except_finger = (ctypes.c_bool * 1)(True)
        self.use_finger = (ctypes.c_bool * 1)(True)
        self.pred = lambda x: True
        self.changed = Event()

    def show(self):
        checked = False
        if ImGui.Checkbox("except finger", self.use_except_finger):
            checked = True
        ImGui.SameLine()
        if ImGui.Checkbox("finger", self.use_finger):
            checked = True

        if checked:
            LOGGER.debug('checked')
            self.changed.fire()

    def mask(self, bone: HumanoidBone) -> bool:
        if self.use_except_finger[0] and self.use_finger[0]:
            return True
        elif self.use_except_finger[0]:
            return not bone.is_finger()
        elif self.use_finger[0]:
            return bone.is_finger()
        else:
            return False
