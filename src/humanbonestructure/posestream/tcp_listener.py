from typing import List
import asyncio
import logging

LOGGER = logging.getLogger(__name__)


class Transport:
    def __init__(self, name: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        self.name = name
        self.reader = reader
        self.writer = writer
        self.error = None
        self.write_bytes = 0

    def __str__(self) -> str:
        if self.error:
            return str(self.error)
        return f'{self.name}:{self.write_bytes}bytes'

    def send(self, data: bytes):
        if self.error:
            return

        self.writer.write(
            b'Content-Type: application/jsonrpc; charset=utf-8\r\n')
        self.writer.write(f'Content-Length: {len(data)}\r\n'.encode('utf-8'))
        self.writer.write(b'\r\n')
        self.writer.write(data)
        self.write_bytes += len(data)

    def set_error(self, error):
        self.error = error


class TcpListener:
    def __init__(self) -> None:
        self.server = None
        self.connections: List[Transport] = []
        self._id = 0
        self.last_data = None

    async def _task(self, port: int):
        self.server = await asyncio.start_server(
            self._handle, '0.0.0.0', port)

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        LOGGER.debug('connected')
        connection = Transport(f'{self._id}', reader, writer)
        self._id += 1
        self.connections.append(connection)
        if self.last_data:
            connection.send(self.last_data)

    def start(self, loop: asyncio.events.AbstractEventLoop, *, port=12721):
        loop.create_task(self._task(port))

    def show(self, p_open):
        if not p_open[0]:
            return
        from pydear import imgui as ImGui
        if ImGui.Begin('tcp_listener', p_open):
            for connection in self.connections:
                ImGui.TextUnformatted(str(connection))
            pass
        ImGui.End()

    def send(self, data: bytes):
        if self.last_data == data:
            return
        for i, connection in enumerate(self.connections):
            try:
                connection.send(data)
            except Exception as ex:
                connection.set_error(ex)

        self.last_data = data
