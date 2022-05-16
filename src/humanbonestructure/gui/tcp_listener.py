from typing import List
import json
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
        self.task = asyncio.get_event_loop().create_task(self.read_async())

    def __str__(self) -> str:
        if self.error:
            return str(self.error)
        return f'{self.name}:{self.write_bytes}bytes'

    async def read_async(self):
        try:
            while not self.reader.at_eof():
                l = await self.reader.readline()
        except Exception as ex:
            LOGGER.warn(ex)
            self.error = ex

    def send(self, data: bytes):
        if self.error:
            return

        try:
            self.writer.write(
                b'Content-Type: application/jsonrpc; charset=utf-8\r\n')
            self.writer.write(
                f'Content-Length: {len(data)}\r\n'.encode('utf-8'))
            self.writer.write(b'\r\n')
            self.writer.write(data)
            self.write_bytes += len(data)
        except Exception as ex:
            LOGGER.warning(ex)
            self.error = ex


class TcpListener:
    def __init__(self) -> None:
        self.server = None
        self.connections: List[Transport] = []
        self._id = 0
        self.last_data = None
        self.port = -1
        self.text = ''

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

    def start(self, loop: asyncio.events.AbstractEventLoop, port: int):
        self.port = port
        loop.create_task(self._task(port))

    def show(self, p_open):
        self.connections = [c for c in self.connections if not c.error]

        if not p_open[0]:
            return

        from pydear import imgui as ImGui
        if ImGui.Begin('tcp_listener', p_open):
            ImGui.TextUnformatted(self.text)
            ImGui.TextUnformatted(f'listen port: {self.port}')
            for connection in self.connections:
                ImGui.TextUnformatted(str(connection))
            pass
        ImGui.End()

    def send(self, data: bytes):
        if self.last_data == data:
            return
        for i, connection in enumerate(self.connections):
            connection.send(data)

        self.last_data = data

    def send_data(self, data: dict):
        from .. import jsonrpc
        self.text = json.dumps(data, indent=2)
        message = jsonrpc.create_notify('strict_tpose', data)
        self.send(json.dumps(message).encode('utf-8'))
