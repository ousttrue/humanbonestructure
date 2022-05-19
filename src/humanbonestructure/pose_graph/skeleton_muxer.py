from typing import Optional
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from ..humanoid.humanoid_skeleton import HumanoidSkeleton


class SkeletonInputPin(InputPin[Optional[HumanoidSkeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'in skeleton')
        self.skeleton = None

    def set_value(self, value: Optional[HumanoidSkeleton]):
        self.skeleton = value


class SkeletonOutputPin(OutputPin[Optional[HumanoidSkeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'out skeleton')

    def get_value(self, node: 'SkeletonMuxerNode') -> Optional[HumanoidSkeleton]:
        return node.in_pin.skeleton


class SkeletonMuxerNode(Node):
    def __init__(self, id: int, input_pin_id: int, out_a: int, out_b: int) -> None:
        self.in_pin = SkeletonInputPin(input_pin_id)
        super().__init__(id, 'skeleton_muxer',
                         [self.in_pin],
                         [SkeletonOutputPin(out_a), SkeletonOutputPin(out_b)])

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("skeleton_muxer"):
            node = SkeletonMuxerNode(
                graph.get_next_id(),
                graph.get_next_id(),
                graph.get_next_id(),
                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'input_pin_id': self.in_pin.id,
            'out_a': self.outputs[0].id,
            'out_b': self.outputs[1].id,
        })
