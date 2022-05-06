from typing import Optional
import logging
import pathlib
import ctypes
from pydear import imgui as ImGui
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from ...formats.bvh.bvh_parser import Bvh
from .file_node import FileNode

LOGGER = logging.getLogger(__name__)


class BvhSkeletonOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def process(self, node: 'BvhNode', input: InputPin):
        if node.bvh:
            input.value = node.bvh


class BvhPoseOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')

    def process(self, node: 'BvhNode', input: InputPin):
        if node.bvh:
            input.value = node.bvh.get_current_pose()


class BvhNode(FileNode):
    '''
    * out: skeleton
    * out: pose
    '''

    def __init__(self, id: int,
                 time_pin_id: int,
                 skeleton_pin_id: int, pose_pin_id: int,
                 path: Optional[pathlib.Path] = None) -> None:
        super().__init__(id, 'bvh', path,
                         [
                             InputPin(time_pin_id, 'time')
                         ],
                         [
                             BvhSkeletonOutputPin(skeleton_pin_id),
                             BvhPoseOutputPin(pose_pin_id)
                         ], '.bvh')
        self.bvh: Optional[Bvh] = None

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'path': str(self.path) if self.path else None,
            'time_pin_id': self.inputs[0].id,
            'skeleton_pin_id': self.outputs[0].id,
            'pose_pin_id': self.outputs[1].id,
        })

    def get_right_indent(self) -> int:
        return 160

    def load(self, path: pathlib.Path):
        self.path = path
        from ...formats.bvh import bvh_parser
        self.bvh = bvh_parser.from_path(path)

    def show_content(self, graph):
        super().show_content(graph)

        if self.bvh:
            for info in self.bvh.get_info():
                ImGui.TextUnformatted(info)

    def process_self(self):
        if not self.bvh and self.path:
            self.load(self.path)

        if self.bvh:
            time_sec = self.inputs[0].value
            if isinstance(time_sec, (int, float)):
                self.bvh.set_time(time_sec)
