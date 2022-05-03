from typing import List, Tuple, Dict, Optional
import ctypes
import logging
import pathlib
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor import NodeEditor, Node, OutputPin, InputPin
from pydear.utils.setting import SettingInterface
from ...scene.scene import Scene


LOGGER = logging.getLogger(__name__)


class PoseGraph(NodeEditor):
    def __init__(self, *, setting: Optional[SettingInterface] = None) -> None:
        super().__init__('pose_graph', setting=setting)
        self.is_initialized = False
        self.nodes: List[Node] = []
        self.links: List[Tuple[int, int]] = []
        self.input_pin_map: Dict[int, Tuple[Node, OutputPin]] = {}
        self.output_pin_map: Dict[int, Tuple[Node, InputPin]] = {}
        self.start_attr = (ctypes.c_int * 1)()
        self.end_attr = (ctypes.c_int * 1)()
        self.process_frame = 0

    def find_output(self, output_id: int) -> Tuple[Node, OutputPin]:
        for node in self.nodes:
            for output in node.outputs:
                if output.id == output_id:
                    return node, output
        raise KeyError()

    def find_input(self, input_id: int) -> Tuple[Node, InputPin]:
        for node in self.nodes:
            for input in node.inputs:
                if input.id == input_id:
                    return node, input
        raise KeyError()

    def connect(self, output_id: int, input_id: int):
        self.links.append((output_id, input_id))
        self.input_pin_map[input_id] = self.find_output(output_id)
        self.output_pin_map[output_id] = self.find_input(input_id)

    def disconnect(self, link_index: int):
        output_id, input_id = self.links[link_index]
        del self.links[link_index]
        del self.input_pin_map[input_id]
        del self.output_pin_map[output_id]

    def on_node_editor(self):
        open_popup = False
        if (ImGui.IsWindowFocused(ImGui.ImGuiFocusedFlags_.RootAndChildWindows) and
                ImNodes.IsEditorHovered()):
            if ImGui.IsMouseClicked(1):
                open_popup = True

        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (8, 8))
        if not ImGui.IsAnyItemHovered() and open_popup:
            ImGui.OpenPopup("add node")

        if ImGui.BeginPopup("add node"):
            click_pos = ImGui.GetMousePosOnOpeningCurrentPopup()
            if ImGui.MenuItem("bvh"):
                from .nodes import BvhNode
                node = BvhNode()
                self.nodes.append(node)
                ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

            ImGui.EndPopup()
        ImGui.PopStyleVar()
