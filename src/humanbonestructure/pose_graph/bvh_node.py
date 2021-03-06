from typing import Optional
import logging
import pathlib
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from ..formats.bvh.bvh_parser import Bvh, Pose
from ..humanoid.bone import Skeleton
from .file_node import FileNode

LOGGER = logging.getLogger(__name__)


class BvhSkeletonOutputPin(OutputPin[Optional[Skeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def get_value(self, node: 'BvhNode') -> Optional[Skeleton]:
        return node.skeleton


class BvhPoseOutputPin(OutputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')

    def get_value(self, node: 'BvhNode') -> Optional[Pose]:
        return node.bvh.get_current_pose() if node.bvh else None


class BvhNode(FileNode):
    '''
    * out: skeleton
    * out: pose
    '''

    def __init__(self, id: int,
                 time_pin_id: int,
                 skeleton_pin_id: int, pose_pin_id: int,
                 path: Optional[pathlib.Path] = None) -> None:
        from .time_node import TimeInputPin
        self.in_time = TimeInputPin(time_pin_id)
        super().__init__(id, 'bvh', path,
                         [
                             self.in_time
                         ],
                         [
                             BvhSkeletonOutputPin(skeleton_pin_id),
                             BvhPoseOutputPin(pose_pin_id)
                         ], '.bvh')
        self.bvh: Optional[Bvh] = None
        self.hierarchy = None
        self.skeleton = None

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("bvh"):
            node = BvhNode(
                graph.get_next_id(),
                graph.get_next_id(),
                graph.get_next_id(),
                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

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
        from ..formats.bvh import bvh_parser
        self.bvh = bvh_parser.from_path(path)
        # scene
        from ..builder import bvh_builder
        self.hierarchy = bvh_builder.build(self.bvh)
        # skeleton
        self.skeleton = self.hierarchy.to_skeleton()

    def show_content(self, graph):
        super().show_content(graph)

        if self.bvh:
            for info in self.bvh.get_info():
                ImGui.TextUnformatted(info)

    def process_self(self):
        if not self.bvh and self.path:
            self.load(self.path)

        if self.bvh:
            time_sec = self.in_time.value
            if isinstance(time_sec, (int, float)):
                self.bvh.set_time(time_sec)
