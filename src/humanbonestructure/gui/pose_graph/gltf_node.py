from typing import Optional
import pathlib
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from ...formats.gltf_loader import Gltf
from ...humanoid.humanoid_skeleton import HumanoidSkeleton
from .file_node import FileNode


class GltfSkeletonOutputPin(OutputPin[Optional[HumanoidSkeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def get_value(self, node: 'GltfNode') -> Optional[HumanoidSkeleton]:
        return node.skeleton


class GltfNode(FileNode):
    '''
    * out: skeleton
    '''

    def __init__(self, id: int, skeleton_pin_id, path: Optional[pathlib.Path] = None) -> None:
        super().__init__(id, 'gltf/glb/vrm', path,
                         [],
                         [
                             GltfSkeletonOutputPin(skeleton_pin_id)
                         ],
                         '.gltf', '.glb', '.vrm')
        self.gltf = None
        self.skeleton = None

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("gltf/glb/vrm"):
            node = GltfNode(
                graph.get_next_id(),
                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

    def get_right_indent(self) -> int:
        return 160

    def to_json(self) -> Serialized:
        return Serialized(self.__class__.__name__, {
            'id': self.id,
            'path': str(self.path) if self.path else None,
            'skeleton_pin_id': self.outputs[0].id,
        })

    def show_content(self, graph):
        super().show_content(graph)

        if self.gltf:
            for info in self.gltf.get_info():
                ImGui.TextUnformatted(info)

    def load(self, path: pathlib.Path):
        self.path = path

        match path.suffix.lower():
            case '.gltf':
                raise NotImplementedError()
            case '.glb' | '.vrm':
                self.gltf = Gltf.load_glb(path.read_bytes())
                from ...scene.builder import gltf_builder
                root = gltf_builder.build(self.gltf)
                self.skeleton = HumanoidSkeleton.from_node(root)

    def process_self(self):
        if not self.gltf and self.path:
            self.load(self.path)
