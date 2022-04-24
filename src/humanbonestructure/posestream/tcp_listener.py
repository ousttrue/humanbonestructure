from typing import List
import asyncio
import logging

LOGGER = logging.getLogger(__name__)


class Transport:
    def __init__(self, name: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        self.name = name
        self.reader = reader
        self.writer = writer


class TcpListener:
    def __init__(self) -> None:
        self.server = None
        self.connections: List[Transport] = []
        self._id = 0

    async def _task(self, port: int):
        self.server = await asyncio.start_server(
            self._handle, '0.0.0.0', port)

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        LOGGER.debug('connected')
        connection = Transport(f'{self._id}', reader, writer)
        self._id += 1
        self.connections.append(connection)

    def start(self, loop: asyncio.events.AbstractEventLoop, *, port=12721):
        loop.create_task(self._task(port))

    def show(self, p_open):
        if not p_open[0]:
            return
        from pydear import imgui as ImGui
        if ImGui.Begin('tcp_listener', p_open):
            for client in self.connections:
                ImGui.TextUnformatted(client.name)
            pass
        ImGui.End()
