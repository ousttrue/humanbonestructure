from pydear import imgui as ImGui
from ..gui.selector import TableSelector
from ..formats.pose import Motion


class MotionSelector(TableSelector[Motion]):
    def __init__(self) -> None:
        from .pose_generator import PoseGenerator
        self.pose_generator = PoseGenerator()
        super().__init__('pose selector',
                         self.pose_generator.motion_list, self.pose_generator.show)
        self.selected += self.pose_generator.set_motion

    def show_selected(self, p_open):
        if not p_open[0]:
            return
        if ImGui.Begin('selected', p_open):
            selected = self.selected.value
            if selected:
                ImGui.TextUnformatted(selected.name)
                ImGui.TextUnformatted(selected.get_info())
                for i, part in enumerate(selected.get_humanboneparts()):
                    if i:
                        ImGui.SameLine()
                    ImGui.TextUnformatted(part.name)
                pass
        ImGui.End()
