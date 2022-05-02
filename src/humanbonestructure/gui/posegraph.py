from typing import List, Tuple, NamedTuple
import logging
import pathlib
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from ..formats.bvh_parser import Bvh
from ..scene.scene import Scene

LOGGER = logging.getLogger(__name__)


class IDGenerator:
    def __init__(self) -> None:
        self.next_id = 1

    def __call__(self) -> int:
        next_id = self.next_id
        self.next_id += 1
        return next_id


ID_GEN = IDGenerator()


class Input:
    def __init__(self, name: str) -> None:
        self.id = ID_GEN()
        self.name = name

    def show(self):
        ImNodes.BeginInputAttribute(self.id)
        ImGui.Text(self.name)
        ImNodes.EndInputAttribute()


class Output:
    def __init__(self, name: str) -> None:
        self.id = ID_GEN()
        self.name = name

    def show(self):
        ImNodes.BeginOutputAttribute(self.id)
        ImGui.Indent(40)
        ImGui.Text(self.name)
        ImNodes.EndOutputAttribute()


class Link(NamedTuple):
    id: int
    begin: Output
    end: Input

    @staticmethod
    def create(src: Output, dst: Input) -> 'Link':
        return Link(ID_GEN(), src, dst)


class Node:
    def __init__(self, name: str) -> None:
        self.id = ID_GEN()
        self.name = name
        self.inputs: List[Input] = []
        self.outputs: List[Output] = []

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


class BvhMotion(Node):
    def __init__(self, bvh: Bvh) -> None:
        super().__init__('bvh motion')
        self.bvh = bvh
        self.out_pose = Output('pose')
        self.outputs.append(self.out_pose)

    def show_content(self):
        ImGui.TextUnformatted(f'bvh: {self.bvh.path.name}')

    def __str__(self):
        return f'T stance, World axis'


class Skeleton(Node):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.scene = Scene(name)
        self.out_skeleton = Output('skeleton')
        self.outputs.append(self.out_skeleton)


class BvhSkeleton(Skeleton):
    def __init__(self, bvh: Bvh) -> None:
        self.bvh = bvh
        super().__init__('bvh skeleton')

    def show_content(self):
        ImGui.TextUnformatted(f'bvh: {self.bvh.path.name}')

    def __str__(self):
        return f'T stance, World axis'


class View(Node):
    '''
    TODO: check compatibility
    '''

    def __init__(self) -> None:
        super().__init__('view')
        self.out_skeleton = Input('skeleton')
        self.inputs.append(self.out_skeleton)
        self.out_pose = Input('pose')
        self.inputs.append(self.out_pose)


class PoseGraph:
    def __init__(self) -> None:
        self.is_initialized = False
        self.nodes: List[Node] = []
        self.links: List[Link] = []

        self.view = View()
        self.nodes.append(self.view)

    def __del__(self):
        if self.is_initialized:
            ImNodes.DestroyContext()
            self.is_initialized = False

    def load_bvh(self, path: pathlib.Path):
        '''
        bvh skeleton-+
                     +--view
        bvh motion---+
        '''
        from ..formats import bvh_parser
        bvh = bvh_parser.from_path(path)
        LOGGER.debug(bvh)

        bvh_motion = BvhMotion(bvh)
        self.links.append(Link.create(bvh_motion.out_pose, self.view.out_pose))
        self.nodes.append(bvh_motion)

        bvh_skeleton = BvhSkeleton(bvh)
        self.links.append(Link.create(
            bvh_skeleton.out_skeleton, self.view.out_skeleton))
        self.nodes.append(bvh_skeleton)

    def show(self, p_open):
        if not p_open[0]:
            return

        if ImGui.Begin("simple node editor", p_open):
            if not self.is_initialized:
                ImNodes.CreateContext()
                self.is_initialized = True

            ImNodes.BeginNodeEditor()

            for node in self.nodes:
                node.show()

            for i, begin, end in self.links:
                ImNodes.Link(i, begin.id, end.id)

            ImNodes.EndNodeEditor()

        ImGui.End()
