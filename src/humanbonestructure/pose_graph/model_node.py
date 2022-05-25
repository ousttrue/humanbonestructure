from typing import Optional, List
import ctypes
import pathlib
import glm
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import InputPin, OutputPin, Serialized
from ..formats.gltf_loader import Gltf
from ..formats.pmd_loader import Pmd
from ..formats.pmx_loader import Pmx
from ..humanoid.bone import Skeleton
from ..humanoid.pose import Pose
from ..builder.hierarchy import Hierarchy
from .file_node import FileNode


class ModelPoseInputPin(InputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')
        self.pose: Optional[Pose] = None

    def set_value(self, pose: Optional[Pose]):
        self.pose = pose


class ModelSkeletonOutputPin(OutputPin[Optional[Skeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def get_value(self, node: 'ModelNode') -> Optional[Skeleton]:
        return node.skeleton


class ModelNode(FileNode):
    '''
    * out: skeleton
    '''

    def __init__(self, id: int, in_pose_id: int, out_skeleton_id: int,
                 path: Optional[pathlib.Path] = None) -> None:
        self.in_pin = ModelPoseInputPin(in_pose_id)
        super().__init__(id, 'gltf/glb/vrm/pmd/pmx', path,
                         [self.in_pin],
                         [ModelSkeletonOutputPin(out_skeleton_id)],
                         '.gltf', '.glb', '.vrm', '.pmd', '.pmx')
        self.model = None
        self.skeleton: Optional[Skeleton] = None
        self.hierarchy: Optional[Hierarchy] = None

        # imgui
        from pydear.utils.fbo_view import FboView
        self.fbo = FboView()
        from ..scene.scene import Scene
        self.scene = Scene(self.fbo.mouse_event)

        # render mesh
        self.fbo.render = self.scene.render

        self.cancel_axis = (ctypes.c_bool * 1)()
        self.strict_delta = (ctypes.c_bool * 1)()

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("gltf/glb/vrm/pmd/pmx"):
            node = ModelNode(
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

        super().show_content(graph)

        if self.scene.skeleton:
            ImGui.Checkbox('cancel axis', self.cancel_axis)
            ImGui.Checkbox('strict delta', self.strict_delta)

    def load(self, path: pathlib.Path):
        self.path = path

        match path.suffix.lower():
            case '.gltf':
                raise NotImplementedError()
            case '.glb' | '.vrm':
                self.model = Gltf.load_glb(path.read_bytes())
                from ..builder import gltf_builder
                hierarchy = gltf_builder.build(self.model)
                self.skeleton = hierarchy.to_skeleton()
                self.hierarchy = hierarchy
            case '.pmd':
                self.model = Pmd(path.read_bytes())
                from ..builder import pmd_builder
                hierarchy = pmd_builder.build(self.model)
                self.skeleton = hierarchy.to_skeleton()
            case '.pmx':
                self.model = Pmx(path.read_bytes())
                from ..builder import pmx_builder
                hierarchy = pmx_builder.build(self.model)
                self.skeleton = hierarchy.to_skeleton()

    def process_self(self):
        if not self.model and self.path:
            self.load(self.path)

        self.scene.update(
            self.skeleton,
            self.in_pin.pose,
            self.hierarchy,
            cancel_axis=self.cancel_axis[0],
            strict_delta=self.strict_delta[0])
