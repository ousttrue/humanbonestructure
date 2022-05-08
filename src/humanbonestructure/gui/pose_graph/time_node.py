import ctypes
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
import time

NS = 1000000000
NS_TO_SEC = 1/1000000000


class TimeOutputPin(OutputPin[float]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'time')

    def get_value(self, node: 'TimeNode') -> float:
        return node.current_time[0]


class TimeInputPin(InputPin[float]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'time')
        self.value = 0.0

    def set_value(self, value: float):
        self.value = value


class TimeNode(Node):
    '''
    TODO: 60FPS frame base ?
    '''

    def __init__(self, id: int, time_pin_id: int, end_time: int, current_time=0) -> None:
        super().__init__(id, 'time', [], [TimeOutputPin(time_pin_id)])
        if current_time > end_time:
            current_time = end_time
        self.current_time = (ctypes.c_float * 1)(current_time)
        self.end_time = (ctypes.c_float * 1)(end_time)
        self.start = None

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("time"):
            node = TimeNode(graph.get_next_id(),
                            graph.get_next_id(), 60)
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

    def get_right_indent(self) -> int:
        return 200

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'time_pin_id': self.outputs[0].id,
            'end_time': self.end_time[0],
            'current_time': self.current_time[0],
        })

    def show_content(self, graph):
        def check_end():
            if self.current_time[0] > self.end_time[0]:
                self.start = None
                self.current_time[0] = self.end_time[0]

        now = time.time_ns()
        if self.start:
            self.current_time[0] = (now - self.start) * NS_TO_SEC
            check_end()

        ImGui.SetNextItemWidth(200)
        if ImGui.SliderFloat('current_time', self.current_time,
                             0, self.end_time[0]):
            if self.start:
                self.start = now - self.current_time[0] * NS
            check_end()
        ImGui.SetNextItemWidth(200)
        if ImGui.InputFloat('end_time', self.end_time):
            check_end()

        if ImGui.Button(chr(0xf95e)):  # rewind
            if self.start:
                self.start = now
            else:
                self.current_time[0] = 0

        ImGui.SameLine()
        if ImGui.Button(chr(0xf9d4)):  # step backward
            pass
        ImGui.SameLine()
        if ImGui.Button(chr(0xf04b)):  # play
            self.start = now - self.current_time[0] * NS
        ImGui.SameLine()
        if ImGui.Button(chr(0xf8e3)):  # pause
            self.start = None
        ImGui.SameLine()
        if ImGui.Button(chr(0xf9d6)):  # step forward
            pass

    def process_self(self):
        pass
