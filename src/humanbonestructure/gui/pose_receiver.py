import logging
import re
import json
from pydear import imgui as ImGui
from ..eventproperty import EventProperty
from ..formats.pose import Pose

LOGGER = logging.getLogger(__name__)


class PoseReceiver:
    def __init__(self) -> None:
        self.pose_event = EventProperty(Pose('empty'))
        self.status = 'init'

    def show(self, p_open):
        if not p_open[0]:
            return
        if ImGui.Begin('receiver', p_open):
            ImGui.TextUnformatted(self.status)
        ImGui.End()

    async def connect_async(self, host: str, port: int):
        import asyncio
        reader, writer = await asyncio.open_connection(host, port)
        self.status = 'connected'

        count = 0

        try:
            while True:
                content_type = await reader.readline()
                content_length = await reader.readline()
                m = re.match(r'^Content-Length: (\d+)\r\n',
                             content_length.decode('utf-8'))
                assert m
                length = int(m.group(1))
                crlf = await reader.readline()
                assert crlf == b'\r\n'

                body = await reader.read(length)
                data = json.loads(body)

                pose = Pose(f'pose{count}')
                self.status = f'pose#{count}'
                count += 1

                self.pose_event.set(pose)
        except Exception as ex:
            self.status = str(ex)
