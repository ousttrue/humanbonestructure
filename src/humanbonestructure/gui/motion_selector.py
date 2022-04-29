from typing import Optional
from pydear import imgui as ImGui
from ..gui.selector import TableSelector
from ..formats.pose import Motion


class MotionSelected:
    def __init__(self) -> None:
        self.selected = None

    def set_motion(self, motion: Optional[Motion]):
        self.selected = motion

    def show(self, p_open):
        if not p_open[0]:
            return
        if ImGui.Begin('motion', p_open):
            if self.selected:
                ImGui.TextUnformatted(self.selected.name)
                ImGui.TextUnformatted(self.selected.get_info())
                for i, part in enumerate(self.selected.get_humanboneparts()):
                    if i:
                        ImGui.SameLine()
                    ImGui.TextUnformatted(part.name)
                pass
        ImGui.End()


class MotionSelector(TableSelector[Motion]):
    def __init__(self) -> None:
        from .pose_generator import PoseGenerator
        self.pose_generator = PoseGenerator()
        super().__init__('pose selector',
                         self.pose_generator.motion_list, self.pose_generator.show)
        self.selected += self.pose_generator.set_motion
