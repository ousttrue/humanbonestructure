from typing import Optional, Dict, Tuple
import ctypes
import pathlib
import glm
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized
from pydear.utils.mouse_event import MouseEvent
from pydear.scene.camera import Camera
from pydear.gizmo.gizmo import Gizmo
from pydear.gizmo.shapes.shape import Shape
from pydear.gizmo.gizmo_select_handler import GizmoSelectHandler
from ...formats.gltf_loader import Gltf
from ...humanoid.humanoid_skeleton import HumanoidSkeleton
from ...humanoid.pose import Pose
from ...humanoid.humanoid_bones import HumanoidBone
from ...humanoid.transform import Transform
from ...scene import scene
from ..bone_shape import BoneShape, Coordinate
from .file_node import FileNode


class GltfPoseInputPin(InputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')
        self.pose: Optional[Pose] = None

    def set_value(self, pose: Optional[Pose]):
        self.pose = pose


class GltfSkeletonOutputPin(OutputPin[Optional[HumanoidSkeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def get_value(self, node: 'GltfNode') -> Optional[HumanoidSkeleton]:
        return node.skeleton


UNITY_CHAN_COORDS = Coordinate(
    yaw=glm.vec3(0, 1, 0),
    pitch=glm.vec3(0, 0, 1),
    roll=glm.vec3(1, 0, 0))


class GizmoScene:
    def __init__(self, mouse_event: MouseEvent) -> None:
        self.mouse_event = mouse_event
        self.camera = Camera(distance=8, y=-0.8)
        self.camera.bind_mouse_event(self.mouse_event)
        self.gizmo = Gizmo()
        self.root: Optional[scene.Node] = None
        self.node_shape_map = {}
        self.pose_conv: Optional[Tuple[Optional[Pose], bool]] = None
        self.tpose_delta_map = {}

        self.drag_handler = GizmoSelectHandler()
        self.drag_handler.bind_mouse_event_with_gizmo(self.mouse_event, self.gizmo)

        def on_selected(selected: Optional[Shape]):
            if selected:
                position = selected.matrix.value[3].xyz
                self.camera.view.set_gaze(position)
        self.drag_handler.selected += on_selected

    def render(self, w: int, h: int):
        mouse_input = self.mouse_event.last_input
        assert(mouse_input)
        self.camera.projection.resize(w, h)
        self.gizmo.process(self.camera, mouse_input.x, mouse_input.y)

    def set_root(self, root: Optional[scene.Node]):
        self.root = root
        if self.root:
            self.root.init_human_bones()
            self.root.calc_bind_matrix(glm.mat4())
            self.root.calc_world_matrix(glm.mat4())
            self.humanoid_node_map = {node.humanoid_bone: node for node,
                                      _ in self.root.traverse_node_and_parent(only_human_bone=True)}
            self.node_shape_map.clear()
            for node, shape in BoneShape.from_root(self.root, self.gizmo, coordinate=UNITY_CHAN_COORDS).items():
                self.node_shape_map[node] = shape

    def set_pose(self, pose: Optional[Pose], convert: bool):
        if not self.root:
            return
        if not self.humanoid_node_map:
            return

        if self.pose_conv == (pose, convert):
            return
        self.pose_conv = (pose, convert)

        self.root.clear_pose()

        if convert:
            if not self.tpose_delta_map:
                # make tpose for pose conversion
                from ...humanoid import tpose
                tpose.make_tpose(self.root)
                self.tpose_delta_map: Dict[HumanoidBone, glm.quat] = {node.humanoid_bone: node.pose.rotation if node.pose else glm.quat(
                ) for node, _ in self.root.traverse_node_and_parent(only_human_bone=True)}
                tpose.local_axis_fit_world(self.root)
                self.root.clear_pose()
        else:
            self.tpose_delta_map.clear()
            self.root.clear_local_axis()

        # assign pose to node hierarchy
        if pose and pose.bones:
            for bone in pose.bones:
                if bone.humanoid_bone:
                    node = self.humanoid_node_map.get(bone.humanoid_bone)
                    if node:
                        if convert:
                            d = self.tpose_delta_map.get(
                                node.humanoid_bone, glm.quat())
                            a = node.local_axis
                            node.pose = Transform.from_rotation(
                                glm.inverse(d) * a * bone.transform.rotation * glm.inverse(a))
                        else:
                            node.pose = bone.transform
                    else:
                        pass
                        # raise RuntimeError()
                else:
                    raise RuntimeError()

        self.root.calc_world_matrix(glm.mat4())

        # sync to gizmo
        for node, shape in self.node_shape_map.items():
            shape.matrix.set(node.world_matrix)


class GltfNode(FileNode):
    '''
    * out: skeleton
    '''

    def __init__(self, id: int, pose_in_pin_id: int, skeleton_out_pin_id: int,
                 path: Optional[pathlib.Path] = None,
                 convert: bool = False) -> None:
        self.in_pin = GltfPoseInputPin(pose_in_pin_id)
        super().__init__(id, 'gltf/glb/vrm', path,
                         [self.in_pin],
                         [GltfSkeletonOutputPin(skeleton_out_pin_id)],
                         '.gltf', '.glb', '.vrm')
        self.gltf = None
        self.skeleton = None

        # imgui
        from pydear.utils.fbo_view import FboView
        self.fbo = FboView()
        self.scene = GizmoScene(self.fbo.mouse_event)
        self.convert = (ctypes.c_bool * 1)(convert)

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
            'pose_in_pin_id': self.in_pin.id,
            'skeleton_out_pin_id': self.outputs[0].id,
            'convert': self.convert[0],
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
        if self.gltf:
            for info in self.gltf.get_info():
                ImGui.TextUnformatted(info)

        ImGui.Checkbox('use convert', self.convert)

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
                self.scene.set_root(root)

    def process_self(self):
        if not self.gltf and self.path:
            self.load(self.path)

        self.scene.set_pose(self.in_pin.pose, self.convert[0])
