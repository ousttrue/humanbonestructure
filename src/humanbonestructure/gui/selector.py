from typing import Optional, List, TypeVar, Generic, Callable
import logging
import abc
from pydear import imgui as ImGui
from .eventproperty import EventProperty


LOGGER = logging.getLogger(__name__)

T = TypeVar('T')


class Filter(EventProperty[Callable[[T], bool]], metaclass=abc.ABCMeta):
    def __init__(self, default_value: Callable[[T], bool]) -> None:
        super().__init__(default_value=default_value)

    @abc.abstractmethod
    def show(self):
        pass


class ItemList(Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[T] = []
        self.filtered_items: List[T] = []

    def __iter__(self):
        return iter(self.filtered_items)

    def filter(self, item: T) -> bool:
        return True

    def apply(self):
        self.filtered_items.clear()
        for item in self.items:
            if self.filter(item):
                self.filtered_items.append(item)


class Selector(Generic[T]):
    def __init__(self, name: str, items: ItemList[T], on_show: Optional[Callable[[], None]]) -> None:
        self.name = name
        self.items = items
        self.selected: EventProperty[Optional[T]] = EventProperty(None)
        self.on_show = on_show

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin(self.name, p_open):
            if self.on_show:
                self.on_show()

            selected = None
            for item in self.items:
                current = ImGui.Selectable(
                    str(item), item == self.selected.value)
                if current:
                    selected = item
            if selected:
                self.selected.set(selected)
        ImGui.End()
