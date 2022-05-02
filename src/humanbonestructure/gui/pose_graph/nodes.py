import ctypes
from typing import List, Dict, Tuple, Callable, Any
from pydear import imnodes as ImNodes
from pydear import imgui as ImGui
from ...formats.bvh_parser import Bvh
from ...scene.scene import Scene


class IDGenerator:
    def __init__(self) -> None:
        self.next_id = 1

    def __call__(self) -> int:
        next_id = self.next_id
        self.next_id += 1
        return next_id


ID_GEN = IDGenerator()


class InputPin:
    def __init__(self, name: str) -> None:
        self.id = ID_GEN()
        self.name = name
        self.value: Any = None

    def show(self):
        ImNodes.BeginInputAttribute(self.id)
        ImGui.Text(self.name)
        ImNodes.EndInputAttribute()


class OutputPin:
    def __init__(self, name: str, process: Callable[[InputPin], None]) -> None:
        self.id = ID_GEN()
        self.name = name
        self.process = process

    def show(self):
        ImNodes.BeginOutputAttribute(self.id)
        ImGui.Indent(40)
        ImGui.Text(self.name)
        ImNodes.EndOutputAttribute()


class Node:
    def __init__(self, name: str) -> None:
        self.process_frame = -1
        self.id = ID_GEN()
        self.name = name
        self.inputs: List[InputPin] = []
        self.outputs: List[OutputPin] = []

    def has_connected_input(self, input_pin_map: Dict[int, Tuple['Node', OutputPin]]) -> bool:
        for input in self.inputs:
            if input.id in input_pin_map:
                return True
        return False

    def has_connected_output(self, ontput_pin_map: Dict[int, Tuple['Node', InputPin]]) -> bool:
        for output in self.outputs:
            if output.id in ontput_pin_map:
                return True
        return False

    def process(self, process_frame: int, input_pin_map: Dict[int, Tuple['Node', OutputPin]]):
        if process_frame == self.process_frame:
            return
        self.process_frame = process_frame

        # update upstream
        for in_pin in self.inputs:
            match input_pin_map.get(in_pin.id):
                case (out_node, out_pin):
                    out_node.process(process_frame, input_pin_map)
                    out_pin.process(in_pin)
                case _:
                    in_pin.value = None

        # self
        self.process_self()

    def process_self(self):
        pass

    def show_content(self):
        pass

    def show(self):
        ImNodes.BeginNode(self.id)

        ImNodes.BeginNodeTitleBar()
        ImGui.TextUnformatted(self.name)
        ImNodes.EndNodeTitleBar()

        self.show_content()

        for input in self.inputs:
            input.show()

        for output in self.outputs:
            output.show()

        ImNodes.EndNode()


class BvhNode(Node):
    def __init__(self, bvh: Bvh) -> None:
        super().__init__('bvh')
        self.bvh = bvh

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

        self.frame = (ctypes.c_int * 1)()

    def show_content(self):
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
