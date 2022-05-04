from typing import List, Dict, Tuple, Callable, Any, Optional
import logging
import pathlib
import ctypes
from pydear import imnodes as ImNodes
from pydear import imgui as ImGui
from ...formats.bvh_parser import Bvh
from ...scene.scene import Scene
from pydear.utils.node_editor import Node, InputPin, OutputPin

LOGGER = logging.getLogger(__name__)
ASSET_DIR: Optional[pathlib.Path] = None


class BvhNode(Node):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'bvh', [], [])
        self.path: Optional[pathlib.Path] = None
        # not pickle
        self.bvh: Optional[Bvh] = None
        self.frame = (ctypes.c_int * 1)()

    def get_right_indent(self) -> int:
        return 160

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle baz
        del state["frame"]
        del state["bvh"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.frame = (ctypes.c_int * 1)()
        if self.path:
            self.load(self.path)

    def _process_skeleton(self, input_pin: InputPin):
        if self.bvh:
            input_pin.value = self.bvh

    def _process_pose(self, input_pin: InputPin):
        if self.bvh:
            input_pin.value = self.bvh.get_current_pose()

    def load(self, path: pathlib.Path, graph=None):
        self.path = path
        from ...formats import bvh_parser
        self.bvh = bvh_parser.from_path(path)

        if graph:
            # skeleton
            self.out_skeleton = OutputPin(
                graph.get_next_id(), 'skeleton', self._process_skeleton)
            self.outputs.append(self.out_skeleton)

            # pose
            self.out_pose = OutputPin(
                graph.get_next_id(), 'pose', self._process_pose)
            self.outputs.append(self.out_pose)

    def show_content(self, graph):
        if ImGui.Button('open'):
            import asyncio

            async def open_task():
                from pydear.utils import filedialog
                selected = await filedialog.open_async(asyncio.get_event_loop(), ASSET_DIR)
                if selected:
                    self.load(selected, graph)
            asyncio.get_event_loop().create_task(open_task())

        if self.bvh:
            ImGui.TextUnformatted(f'bvh: {self.bvh.path.name}')
            end_frame = self.bvh.get_frame_count()-1
            ImGui.TextUnformatted(self.bvh.get_info())
            ImGui.SetNextItemWidth(200)
            if ImGui.SliderInt('frame', self.frame, 0, end_frame):
                self.bvh.set_frame(self.frame[0])

    def __str__(self):
        return f'T stance, World axis'


# class View(Node):
#     def __init__(self, scene: Scene) -> None:
#         super().__init__('view')
#         self.scene = scene
#         self.in_skeleton = InputPin('skeleton')
#         self.inputs.append(self.in_skeleton)
#         self.in_pose = InputPin('pose')
#         self.inputs.append(self.in_pose)

#         self.skeleton = None
#         self.pose = None

#     def process_self(self):
#         if self.in_skeleton.value != self.skeleton:
#             # update skeleton
#             self.skeleton = self.in_skeleton.value
#             self.scene.load(self.skeleton)

#         if self.in_pose.value != self.pose:
#             # update pose
#             self.pose = self.in_pose.value
#             self.scene.set_pose(self.in_pose.value)
