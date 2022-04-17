from typing import Optional, List, TypeVar, Generic, Callable
import logging
import abc
from pydear import imgui as ImGui
from .eventproperty import EventProperty


LOGGER = logging.getLogger(__name__)

T = TypeVar('T')


class Filter(EventProperty[Callable[[T], bool]], metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        super().__init__(lambda _: True)

    @abc.abstractmethod
    def show(self):
        pass


class Selector(Generic[T]):
    def __init__(self, name: str, filter: Filter[T]) -> None:
        self.name = name
        self.items: List[T] = []
        self.filter = filter
        self.filter += self.apply

        self.filtered_items: List[T] = []
        self.selected: EventProperty[Optional[T]] = EventProperty(None)

    def apply(self, filter=None):
        self.filtered_items.clear()
        for item in self.items:
            if not filter or filter(item):
                self.filtered_items.append(item)

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin(self.name, p_open):
            self.filter.show()

            selected = None
            for item in self.filtered_items:
                current = ImGui.Selectable(
                    str(item), item == self.selected.value)
                if current:
                    selected = item
            if selected:
                self.selected.set(selected)
        ImGui.End()
