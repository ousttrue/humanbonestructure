from typing import Optional
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from ...humanoid.pose import Pose


class PoseInputPin(InputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'in pose')
        self.pose = None

    def set_value(self, value: Optional[Pose]):
        self.pose = value


class PoseOutputPin(OutputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'out pose')

    def get_value(self, node: 'PoseMuxerNode') -> Optional[Pose]:
        return node.in_pin.pose


class PoseMuxerNode(Node):
    def __init__(self, id: int, input_pin_id: int, out_a: int, out_b: int) -> None:
        self.in_pin = PoseInputPin(input_pin_id)
        super().__init__(id, 'pose_muxer',
                         [self.in_pin],
                         [PoseOutputPin(out_a), PoseOutputPin(out_b)])

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("pose_muxer"):
            node = PoseMuxerNode(
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
