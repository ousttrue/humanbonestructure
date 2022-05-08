from typing import Optional, List, Union
import pathlib
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from ...formats.pmd_loader import Pmd
from ...formats.pmx_loader import Pmx
from ...humanoid.humanoid_skeleton import HumanoidSkeleton
from .file_node import FileNode


class MmdSkeletonOutputPin(OutputPin[Optional[HumanoidSkeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def get_value(self, node: 'MmdModelNode') -> Optional[HumanoidSkeleton]:
        return node.skeleton


class MmdModelNode(FileNode):
    def __init__(self, id: int, skeleton_pin_id: int, path: Optional[pathlib.Path] = None) -> None:
        super().__init__(id, 'pmd/pmx', path,
                         [],
                         [
                             MmdSkeletonOutputPin(skeleton_pin_id)
                         ], '.pmd', '.pmx')
        self.pmd_pmx = None
        self.skeleton: Optional[HumanoidSkeleton] = None

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("pmd/pmx"):
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
                pmd = Pmd(path.read_bytes())
                self.pmd_pmx = pmd
                from ...scene.builder import pmd_builder
                root = pmd_builder.build(pmd)
                self.skeleton = HumanoidSkeleton.from_node(
                    root, is_inverted_pelvis=True)
            case '.pmx':
                pmx = Pmx(path.read_bytes())
                self.pmd_pmx = pmx
                from ...scene.builder import pmx_builder
                root = pmx_builder.build(pmx)
                self.skeleton = HumanoidSkeleton.from_node(
                    root, is_inverted_pelvis=True)

    def process_self(self):
        if not self.skeleton and self.path:
            self.load(self.path)
