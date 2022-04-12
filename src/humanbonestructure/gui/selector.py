from typing import Optional, Any

from pydear import imgui as ImGui


class Selector:
    def __init__(self, on_selected) -> None:
        self.items = []
        self.selected: Optional[Any] = None
        self.on_selected = on_selected

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin("select vpd", p_open):
            selected = None
            for item in self.items:
                current = ImGui.Selectable(
                    str(item), item == self.selected)
                if current:
                    selected = item
            if selected:
                self.selected = selected
                self.on_selected(selected)
        ImGui.End()
