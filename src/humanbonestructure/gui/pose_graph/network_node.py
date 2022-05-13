from typing import Optional
import ctypes
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from ...humanoid.pose import Pose


class TcpClientPoseOutputPin(OutputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')

    def get_value(self, node: 'TcpClientNode') -> Optional[Pose]:
        return node.pose


class TcpClientNode(Node):
    def __init__(self, id: int, pose_pin_id: int,  port: int = 12727) -> None:
        super().__init__(id, 'tcp_client',
                         [
                         ],
                         [
                             TcpClientPoseOutputPin(pose_pin_id)
                         ])
        self.port = (ctypes.c_int * 1)(port)
        self.pose = None
        self.status = 'not connected'

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("tcp client"):
            node = TcpClientNode(
                graph.get_next_id(),
                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'port': self.port[0],
            'pose_pin_id': self.outputs[0].id,
        })

    def show_content(self, graph):
        ImGui.SetNextItemWidth(200)
        ImGui.InputInt('port', self.port)
        ImGui.TextUnformatted(self.status)



