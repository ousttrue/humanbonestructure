from typing import Optional
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from ..scene import node
from ..humanoid.bone import Skeleton


class TPoseSkeletonOutputPin(OutputPin[Skeleton]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def get_value(self, node: 'TPoseNode') -> Skeleton:
        return node.skeleton


class TPoseNode(Node):
    def __init__(self, id: int, skeleton_pin_id: int) -> None:
        super().__init__(id, 'strict TPose',
                         [],
                         [
                             TPoseSkeletonOutputPin(skeleton_pin_id)
                         ])
        self.skeleton = Skeleton.create_default()

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("tpose"):
            node = TPoseNode(
                graph.get_next_id(),
                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

    def get_right_indent(self) -> int:
        return 80

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'skeleton_pin_id': self.outputs[0].id,
        })
