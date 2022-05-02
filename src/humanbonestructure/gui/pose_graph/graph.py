from typing import List, Tuple, Dict
import ctypes
import logging
import pathlib
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from ...scene.scene import Scene
from .nodes import Node, View, OutputPin, InputPin

LOGGER = logging.getLogger(__name__)


class PoseGraph:
    def __init__(self, scene: Scene, ini_file: pathlib.Path) -> None:
        self.ini_file = ini_file
        self.is_initialized = False
        self.nodes: List[Node] = []
        self.links: List[Tuple[int, int]] = []
        self.input_pin_map: Dict[int, Tuple[Node, OutputPin]] = {}
        self.output_pin_map: Dict[int, Tuple[Node, InputPin]] = {}

        self.view = View(scene)
        self.nodes.append(self.view)

        self.start_attr = (ctypes.c_int * 1)()
        self.end_attr = (ctypes.c_int * 1)()

        self.process_frame = 0

    def __del__(self):
        if self.is_initialized:
            self.save(self.ini_file)
            ImNodes.DestroyContext()
            self.is_initialized = False

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

    def load_bvh(self, path: pathlib.Path):
        '''
        bvh skeleton-+
                     +--view
        bvh motion---+
        '''
        from ...formats import bvh_parser
        bvh = bvh_parser.from_path(path)
        LOGGER.debug(bvh)

        from .nodes import BvhNode
        bvh_motion = BvhNode(bvh)
        self.nodes.append(bvh_motion)

    def show(self, p_open):
        if not p_open[0]:
            return

        if ImGui.Begin("simple node editor", p_open):
            if not self.is_initialized:
                ImNodes.CreateContext()
                self.load(self.ini_file)
                ImNodes.PushAttributeFlag(
                    ImNodes.ImNodesAttributeFlags_.EnableLinkDetachWithDragClick)
                self.is_initialized = True

            ImNodes.BeginNodeEditor()

            for node in self.nodes:
                node.show()

            for i, (begin, end) in enumerate(self.links):
                ImNodes.Link(i, begin, end)

            ImNodes.EndNodeEditor()

            # update link
            if ImNodes.IsLinkCreated(self.start_attr, self.end_attr):
                self.connect(self.start_attr[0], self.end_attr[0])
            if ImNodes.IsLinkDestroyed(self.start_attr):
                self.disconnect(self.start_attr[0])

            # data flow
            process_frame = self.process_frame
            self.process_frame += 1
            for node in self.nodes:
                if not node.has_connected_output(self.output_pin_map):
                    node.process(process_frame, self.input_pin_map)

        ImGui.End()

    def save(self, path: pathlib.Path):
        # Save the internal imnodes state
        ImNodes.SaveCurrentEditorStateToIniFile(str(path))

    def load(self, path: pathlib.Path):
        # Load the internal imnodes state
        ImNodes.LoadCurrentEditorStateFromIniFile(str(path))
