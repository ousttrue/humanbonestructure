from typing import Optional, Union
import ctypes
import pathlib
from pydear import imgui as ImGui
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from ...formats.vmd_loader import Vmd
from ...formats.vpd_loader import Vpd


ASSET_DIR: Optional[pathlib.Path] = None


class MmdPoseOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')

    def process(self, node: 'MmdPoseNode', input: InputPin):
        if node.vpd_vmd:
            input.value = node.vpd_vmd.get_current_pose()


class MmdPoseNode(Node):
    def __init__(self, id: int, pose_pin_id: int, path: Optional[pathlib.Path] = None) -> None:
        super().__init__(id, 'vmd/vpd', [], [
            MmdPoseOutputPin(pose_pin_id)
        ])
        if isinstance(path, str):
            path = pathlib.Path(path)
        self.path: Optional[pathlib.Path] = path
        self.vpd_vmd: Union[Vmd, Vpd, None] = None
        self.frame = (ctypes.c_int * 1)()

    def to_json(self) -> Serialized:
        return Serialized('MmdPoseNode', {
            'id': self.id,
            'path': str(self.path) if self.path else None,
            'pose_pin_id': self.outputs[0].id,
        })

    def __str__(self):
        return f'A stance, World axis'

    def get_right_indent(self) -> int:
        return 160

    def load(self, path: pathlib.Path):
        self.path = path

        match path.suffix.lower():
            case '.vpd':
                self.vpd_vmd = Vpd.load(path.name, path.read_bytes())
                self.frame[0] = 0

            case '.vmd':
                self.vpd_vmd = Vmd.load(path.name, path.read_bytes())
                if self.frame[0] >= self.vpd_vmd.get_frame_count():
                    self.frame[0] = self.vpd_vmd.get_frame_count()-1

    def show_content(self, graph):
        if ImGui.Button('open'):
            import asyncio

            async def open_task():
                from pydear.utils import filedialog
                dir = self.path.parent if self.path else graph.current_dir
                selected = await filedialog.open_async(asyncio.get_event_loop(), dir, filter=filedialog.Filter('.vmd', '.vpd'))
                if selected:
                    self.load(selected)
            asyncio.get_event_loop().create_task(open_task())

        if self.vpd_vmd:
            ImGui.TextUnformatted(f'vmd/vpd: {self.vpd_vmd.name}')
            end_frame = self.vpd_vmd.get_frame_count()-1
            for info in self.vpd_vmd.get_info():
                ImGui.TextUnformatted(info)
            ImGui.SetNextItemWidth(200)
            if ImGui.SliderInt('frame', self.frame, 0, end_frame):
                self.vpd_vmd.set_frame(self.frame[0])

    def process_self(self):
        if not self.vpd_vmd and self.path:
            self.load(self.path)
