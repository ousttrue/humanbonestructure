from typing import Optional, List
import logging
from pydear import imgui as ImGui
from ..formats.vpd_loader import Vpd
from .eventproperty import EventProperty

LOGGER = logging.getLogger(__name__)


class Selector:
    def __init__(self, name: str, filter: EventProperty) -> None:
        self.name = name
        self.items: List[Vpd] = []
        self.filter = filter
        self.filter += self.apply

        assert filter.show
        self.show_filter = filter.show

        self.filtered_items: List[Vpd] = []
        self.selected: EventProperty[Optional[Vpd]] = EventProperty(None)

    def apply(self, filter=None):
        self.filtered_items.clear()
        for item in self.items:
            if not filter or filter(item):
                self.filtered_items.append(item)

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin(self.name, p_open):
            self.show_filter()

            selected = None
            for item in self.filtered_items:
                current = ImGui.Selectable(
                    str(item), item == self.selected.value)
                if current:
                    selected = item
            if selected:
                self.selected.set(selected)
        ImGui.End()
