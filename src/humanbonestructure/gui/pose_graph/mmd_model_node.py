from typing import Optional, List
import pathlib
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from .file_node import FileNode
from pydear import imgui as ImGui


class MmdSkeletonOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def process(self, node: 'MmdModelNode', input: InputPin):
        if node.pmd_pmx:
            input.value = node.pmd_pmx


class MmdModelNode(FileNode):
    def __init__(self, id: int, skeleton_pin_id: int, path: Optional[pathlib.Path] = None) -> None:
        super().__init__(id, 'pmd/pmx', path,
                         [],
                         [
                             MmdSkeletonOutputPin(skeleton_pin_id)
                         ], '.pmd', '.pmx')
        self.pmd_pmx = None

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
                from ...formats import pmd_loader
                self.pmd_pmx = pmd_loader.Pmd(path.read_bytes())
            case '.pmx':
                from ...formats import pmx_loader
                self.pmd_pmx = pmx_loader.Pmx(path.read_bytes())

    def process_self(self):
        if not self.pmd_pmx and self.path:
            self.load(self.path)
