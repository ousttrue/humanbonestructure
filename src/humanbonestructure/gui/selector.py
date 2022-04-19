from typing import Optional, List, TypeVar, Generic, Callable, Iterable, NamedTuple
import logging
import abc
from pydear import imgui as ImGui
from ..eventproperty import EventProperty, OptionalEventProperty


LOGGER = logging.getLogger(__name__)

T = TypeVar('T')


class Filter(EventProperty[Callable[[T], bool]], metaclass=abc.ABCMeta):
    def __init__(self, default_value: Callable[[T], bool]) -> None:
        super().__init__(default_value=default_value)

    @abc.abstractmethod
    def show(self):
        pass


class Header(NamedTuple):
    name: str
    width: Optional[float] = None


class ItemList(Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[T] = []
        self.filtered_items: List[T] = []
        self.headers: List[Header] = [Header('name')]

    def __iter__(self):
        return iter(self.filtered_items)

    def columns(self, item: T) -> Iterable[str]:
        raise NotImplementedError()

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
        self.selected: OptionalEventProperty[T] = OptionalEventProperty()
        self.on_show = on_show

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin(self.name, p_open):
            if self.on_show:
                self.on_show()

            self._selector()
        ImGui.End()

    def _selector(self):
        selected = None
        for item in self.items:
            current = ImGui.Selectable(
                str(item), item == self.selected.value)
            if current:
                selected = item
        if selected:
            self.selected.set(selected)


class TableSelector(Generic[T]):
    def __init__(self, name: str, items: ItemList[T], on_show: Optional[Callable[[], None]]) -> None:
        self.name = name
        self.items = items
        self.selected: OptionalEventProperty[T] = OptionalEventProperty()
        self.on_show = on_show

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin(self.name, p_open):
            if self.on_show:
                self.on_show()

            self._selector()
        ImGui.End()

    def _selector(self):
        # tree
        flags = (
            ImGui.ImGuiTableFlags_.BordersV
            | ImGui.ImGuiTableFlags_.BordersOuterH
            | ImGui.ImGuiTableFlags_.Resizable
            | ImGui.ImGuiTableFlags_.RowBg
            | ImGui.ImGuiTableFlags_.NoBordersInBody
        )
        if ImGui.BeginTable(self.name, len(self.items.headers), flags):
            # header
            for header in self.items.headers:
                match header:
                    case Header(label, width):
                        if isinstance(width, (float, int)):
                            ImGui.TableSetupColumn(
                                label, ImGui.ImGuiTableColumnFlags_.WidthFixed, width)
                        else:
                            ImGui.TableSetupColumn(label)
                    case _:
                        ImGui.TableSetupColumn(header)
            ImGui.TableHeadersRow()

            selected = None

            # body
            for item in self.items:
                ImGui.TableNextRow()
                for i, col in enumerate(self.items.columns(item)):
                    ImGui.TableNextColumn()
                    if i == 0:
                        current = ImGui.Selectable(
                            col, item == self.selected.value)
                        if current:
                            selected = item
                    else:
                        #
                        ImGui.TextUnformatted(col)

            if selected:
                self.selected.set(selected)

            ImGui.EndTable()

        selected = None
