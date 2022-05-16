from typing import Optional
from enum import Enum, auto
import logging
import asyncio
import ctypes
import json
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from ...humanoid.pose import Pose
from ... import jsonrpc


LOGGER = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    NotConnected = auto()
    Connecting = auto()
    Connected = auto()


class TcpClientPoseOutputPin(OutputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')

    def get_value(self, node: 'TcpClientNode') -> Optional[Pose]:
        return node.pose


class TcpClientNode(Node):
    def __init__(self, id: int, pose_pin_id: int,  port: int = 12721) -> None:
        super().__init__(id, 'tcp_client',
                         [
                         ],
                         [
                             TcpClientPoseOutputPin(pose_pin_id)
                         ])
        self.port = (ctypes.c_int * 1)(port)
        self.pose = None
        self.status = ConnectionStatus.NotConnected
        self.tasks = []
        self.receive_count = 0

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

    async def connect_async(self, port: int, *, host='127.0.0.1'):
        self.status = ConnectionStatus.Connecting
        reader, writer = await asyncio.open_connection(host, port)
        self.status = ConnectionStatus.Connected
        LOGGER.debug(f'connected: {host}:{port}')

        try:
            while not reader.at_eof():
                data_length = 0
                while True:
                    l = await reader.readline()
                    line = l.decode('utf-8').rstrip()
                    if line == '':
                        break
                    key, value = line.split(':', 1)
                    match key:
                        case 'Content-Length':
                            data_length = int(value)
                        case 'Content-Type':
                            pass
                        case _:
                            LOGGER.warn(f'unknown header: {line}')
                assert data_length

                body = await reader.read(data_length)
                self.dispatch(json.loads(body))

        except Exception as ex:
            LOGGER.exception(ex)
            self.status = ConnectionStatus.NotConnected

    def dispatch(self, message: dict):
        match message:
            case {'method': method, 'params': param}:
                self.pose = Pose.from_json(f'pose#{self.receive_count}', param)
                self.receive_count += 1

            case _:
                LOGGER.warn(message)

    def show_content(self, graph):
        ImGui.SetNextItemWidth(200)
        ImGui.InputInt('port', self.port)
        ImGui.TextUnformatted(f'{self.status.name}#{self.receive_count}')

        if ImGui.Button('connect'):
            loop = asyncio.get_event_loop()
            self.tasks.append(loop.create_task(
                self.connect_async(self.port[0])))
