from typing import Optional
import ctypes
import pathlib
import glm
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from ..formats.gltf_loader import Gltf
from ..humanoid.bone import Skeleton
from ..humanoid.pose import Pose
from .file_node import FileNode


class GltfPoseInputPin(InputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')
        self.pose: Optional[Pose] = None

    def set_value(self, pose: Optional[Pose]):
        self.pose = pose


class GltfSkeletonOutputPin(OutputPin[Optional[Skeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def get_value(self, node: 'GltfNode') -> Optional[Skeleton]:
        return node.skeleton


class GltfNode(FileNode):
    '''
    * out: skeleton
    '''

    def __init__(self, id: int, in_pose_id: int, out_skeleton_id: int,
                 path: Optional[pathlib.Path] = None) -> None:
        self.in_pin = GltfPoseInputPin(in_pose_id)
        super().__init__(id, 'gltf/glb/vrm', path,
                         [self.in_pin],
                         [GltfSkeletonOutputPin(out_skeleton_id)],
                         '.gltf', '.glb', '.vrm')
        self.gltf = None
        self.skeleton: Optional[Skeleton] = None

        # imgui
        from pydear.utils.fbo_view import FboView
        self.fbo = FboView()
        from ..scene.node_scene import NodeScene
        self.scene = NodeScene(self.fbo.mouse_event)
        self.cancel_axis = (ctypes.c_bool * 1)()
        self.strict_delta = (ctypes.c_bool * 1)()

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("gltf/glb/vrm"):
            node = GltfNode(
                graph.get_next_id(),
                graph.get_next_id(),
                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'path': str(self.path) if self.path else None,
            'in_pose_id': self.in_pin.id,
            'out_skeleton_id': self.outputs[0].id,
        })

    def get_right_indent(self) -> int:
        return 360

    def show_content(self, graph):
        w = 400
        h = 400
        x, y = ImNodes.GetNodeScreenSpacePos(self.id)
        y += 43
        x += 8
        self.fbo.show_fbo(x, y, w, h)

        # render mesh
        assert self.fbo.mouse_event.last_input
        self.scene.render(w, h)

        super().show_content(graph)
        # if self.gltf:
        #     for info in self.gltf.get_info():
        #         ImGui.TextUnformatted(info)

        if self.scene.skeleton:
            ImGui.Checkbox('cancel axis', self.cancel_axis)
            ImGui.Checkbox('strict delta', self.strict_delta)

    def load(self, path: pathlib.Path):
        self.path = path

        match path.suffix.lower():
            case '.gltf':
                raise NotImplementedError()
            case '.glb' | '.vrm':
                self.gltf = Gltf.load_glb(path.read_bytes())
                from ..scene.builder import gltf_builder
                root = gltf_builder.build(self.gltf)
                self.skeleton = root.to_skeleton()
                self.cancel_skeleton = root.to_skeleton()

    def process_self(self):
        if not self.gltf and self.path:
            self.load(self.path)

        self.scene.update(
            self.skeleton,
            self.in_pin.pose,
            cancel_axis=self.cancel_axis[0],
            strict_delta=self.strict_delta[0])
