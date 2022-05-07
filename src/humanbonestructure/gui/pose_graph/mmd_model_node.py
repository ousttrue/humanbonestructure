from typing import Optional, List, Union
import pathlib
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from ...formats.pmd_loader import Pmd
from ...formats.pmx_loader import Pmx
from .file_node import FileNode


class MmdSkeletonOutputPin(OutputPin[Union[Pmd, Pmx, None]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def get_value(self, node: 'MmdModelNode'):
        return node.pmd_pmx


class MmdModelNode(FileNode):
    def __init__(self, id: int, skeleton_pin_id: int, path: Optional[pathlib.Path] = None) -> None:
        super().__init__(id, 'pmd/pmx', path,
                         [],
                         [
                             MmdSkeletonOutputPin(skeleton_pin_id)
                         ], '.pmd', '.pmx')
        self.pmd_pmx = None

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("pmd/pmx"):
            from .mmd_model_node import MmdModelNode
            node = MmdModelNode(graph.get_next_id(),
                                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

    def get_right_indent(self) -> int:
        return 160

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'path': str(self.path) if self.path else None,
            'skeleton_pin_id': self.outputs[0].id,
        })

    def show_content(self, graph):
        super().show_content(graph)

        if self.pmd_pmx:
            for info in self.pmd_pmx.get_info():
                ImGui.TextUnformatted(info)

    def load(self, path: pathlib.Path):
        self.path = path

        match path.suffix.lower():
            case '.pmd':
                self.pmd_pmx = Pmd(path.read_bytes())
            case '.pmx':
                self.pmd_pmx = Pmx(path.read_bytes())

    def process_self(self):
        if not self.pmd_pmx and self.path:
            self.load(self.path)
