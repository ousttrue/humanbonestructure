from typing import List, Dict, Tuple, Callable, Any, Optional
import pathlib
import ctypes
from pydear import imnodes as ImNodes
from pydear import imgui as ImGui
from ...formats.bvh_parser import Bvh
from ...scene.scene import Scene
from pydear.utils.node_editor import Node, InputPin, OutputPin

# def load_bvh(self, path: pathlib.Path):
#     '''
#     bvh skeleton-+
#                  +--view
#     bvh motion---+
#     '''
#     from ...formats import bvh_parser
#     bvh = bvh_parser.from_path(path)
#     LOGGER.debug(bvh)

#     # bvh_motion = BvhNode(bvh)
#     # self.nodes.append(bvh_motion)


class BvhNode(Node):
    def __init__(self) -> None:
        super().__init__('bvh', [], [])
        self.bvh: Optional[Bvh] = None
        self.frame = (ctypes.c_int * 1)()

    def load(self, path: pathlib.Path):
        # skeleton
        def process_skeleton(input_pin: InputPin):
            input_pin.value = self.bvh
        self.out_skeleton = OutputPin('skeleton', process_skeleton)
        self.outputs.append(self.out_skeleton)

        # pose
        def process_pose(input_pin: InputPin):
            input_pin.value = self.bvh.get_current_pose()
        self.out_pose = OutputPin('pose', process_pose)
        self.outputs.append(self.out_pose)

    def show_content(self):
        if ImGui.Button('open'):
            # file dialog
            pass

        if self.bvh:
            ImGui.TextUnformatted(f'bvh: {self.bvh.path.name}')
            end_frame = self.bvh.get_frame_count()-1
            ImGui.TextUnformatted(self.bvh.get_info())
            if ImGui.SliderInt('frame', self.frame, 0, end_frame):
                self.bvh.set_frame(self.frame[0])

    def __str__(self):
        return f'T stance, World axis'


class View(Node):
    def __init__(self, scene: Scene) -> None:
        super().__init__('view')
        self.scene = scene
        self.in_skeleton = InputPin('skeleton')
        self.inputs.append(self.in_skeleton)
        self.in_pose = InputPin('pose')
        self.inputs.append(self.in_pose)

        self.skeleton = None
        self.pose = None

    def process_self(self):
        if self.in_skeleton.value != self.skeleton:
            # update skeleton
            self.skeleton = self.in_skeleton.value
            self.scene.load(self.skeleton)

        if self.in_pose.value != self.pose:
            # update pose
            self.pose = self.in_pose.value
            self.scene.set_pose(self.in_pose.value)
