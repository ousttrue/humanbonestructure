from typing import Optional
import logging
import pathlib
import ctypes
from pydear import imgui as ImGui
from pydear import imgui_internal
from pydear import imnodes as ImNodes
from ...formats.bvh.bvh_parser import Bvh
from ...scene.scene import Scene
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized

LOGGER = logging.getLogger(__name__)


ASSET_DIR: Optional[pathlib.Path] = None


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


class BvhNode(Node):
    def __init__(self, id: int, skeleton_pin_id: int, pose_pin_id: int, path: Optional[pathlib.Path] = None) -> None:
        super().__init__(id, 'bvh', [], [])
        if isinstance(path, str):
            path = pathlib.Path(path)
        self.path: Optional[pathlib.Path] = path
        # skeleton
        out_skeleton = BvhSkeletonOutputPin(skeleton_pin_id)
        self.outputs.append(out_skeleton)
        # pose
        out_pose = BvhPoseOutputPin(pose_pin_id)
        self.outputs.append(out_pose)

        self.bvh: Optional[Bvh] = None
        self.frame = (ctypes.c_int * 1)()

    def to_json(self) -> Serialized:
        return Serialized('BvhNode', {
            'id': self.id,
            'path': str(self.path) if self.path else None,
            'skeleton_pin_id': self.outputs[0].id,
            'pose_pin_id': self.outputs[1].id,
        })

    def __str__(self):
        return f'T stance, World axis'

    def get_right_indent(self) -> int:
        return 160

    def load(self, path: pathlib.Path):
        self.path = path
        from ...formats.bvh import bvh_parser
        self.bvh = bvh_parser.from_path(path)
        if self.frame[0] >= self.bvh.frame_count:
            self.frame[0] = self.bvh.frame_count-1

    def show_content(self, graph):
        if ImGui.Button('open'):
            import asyncio

            async def open_task():
                from pydear.utils import filedialog
                dir = self.path.parent if self.path else ASSET_DIR
                selected = await filedialog.open_async(asyncio.get_event_loop(), dir)
                if selected:
                    self.load(selected)
            asyncio.get_event_loop().create_task(open_task())

        if self.bvh:
            ImGui.TextUnformatted(f'bvh: {self.bvh.path.name}')
            end_frame = self.bvh.get_frame_count()-1
            for info in self.bvh.get_info():
                ImGui.TextUnformatted(info)
            ImGui.SetNextItemWidth(200)
            if ImGui.SliderInt('frame', self.frame, 0, end_frame):
                self.bvh.set_frame(self.frame[0])

    def process_self(self):
        if not self.bvh and self.path:
            self.load(self.path)
