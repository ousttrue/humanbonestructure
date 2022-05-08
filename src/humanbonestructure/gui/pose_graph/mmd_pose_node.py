from typing import Optional, Union
import ctypes
import pathlib
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from ...humanoid.pose import Pose
from ...formats.vmd_loader import Vmd
from ...formats.vpd_loader import Vpd
from .file_node import FileNode

ASSET_DIR: Optional[pathlib.Path] = None


class MmdPoseOutputPin(OutputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')

    def get_value(self, node: 'MmdPoseNode') -> Optional[Pose]:
        return node.vpd_vmd.get_current_pose() if node.vpd_vmd else None


class MmdPoseNode(FileNode):
    def __init__(self, id: int,
                 input_pin_id: int,
                 pose_pin_id: int, path: Optional[pathlib.Path] = None) -> None:
        from .time_node import TimeInputPin
        self.in_time = TimeInputPin(input_pin_id)
        super().__init__(id, 'vmd/vpd', path,
                         [
                             self.in_time
                         ],
                         [
                             MmdPoseOutputPin(pose_pin_id)
                         ],
                         '.vmd', '.vpd')
        self.vpd_vmd: Union[Vmd, Vpd, None] = None
        self.frame = (ctypes.c_int * 1)()

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("vmd/vpd"):
            from .mmd_pose_node import MmdPoseNode
            node = MmdPoseNode(
                graph.get_next_id(),
                graph.get_next_id(),
                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'path': str(self.path) if self.path else None,
            'input_pin_id': self.in_time.id,
            'pose_pin_id': self.outputs[0].id,
        })

    def get_right_indent(self) -> int:
        return 160

    def load(self, path: pathlib.Path):
        self.path = path

        match path.suffix.lower():
            case '.vpd':
                self.vpd_vmd = Vpd.load(path.name, path.read_bytes())
            case '.vmd':
                self.vpd_vmd = Vmd.load(path.name, path.read_bytes())

    def show_content(self, graph):
        super().show_content(graph)

        if self.vpd_vmd:
            for info in self.vpd_vmd.get_info():
                ImGui.TextUnformatted(info)

    def process_self(self):
        if not self.vpd_vmd and self.path:
            self.load(self.path)

        if self.vpd_vmd:
            time_sec = self.in_time.value
            if isinstance(time_sec, (int, float)):
                self.vpd_vmd.set_time(time_sec)
