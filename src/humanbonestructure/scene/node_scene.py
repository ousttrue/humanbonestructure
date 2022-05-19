from typing import Optional, Tuple, Dict
import glm
from pydear.utils.mouse_event import MouseEvent
from pydear.scene.camera import Camera
from pydear.gizmo.gizmo import Gizmo
from pydear.gizmo.gizmo_select_handler import GizmoSelectHandler
from pydear.gizmo.shapes.shape import Shape
from ..humanoid.pose import Pose
from ..humanoid.humanoid_bones import HumanoidBone
from ..humanoid.transform import Transform
from .unitychan_coords import get_unitychan_coords
from .node import Node
from .bone_shape import BoneShape


class NodeScene:
    def __init__(self, mouse_event: MouseEvent) -> None:
        self.mouse_event = mouse_event
        self.camera = Camera(distance=8, y=-0.8)
        self.camera.bind_mouse_event(self.mouse_event)
        self.gizmo = Gizmo()
        self.root: Optional[Node] = None
        self.node_shape_map = {}
        self.pose_conv: Optional[Tuple[Optional[Pose], bool]] = None
        self.tpose_delta_map = {}

        self.drag_handler = GizmoSelectHandler()
        self.drag_handler.bind_mouse_event_with_gizmo(
            self.mouse_event, self.gizmo)

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

    def set_root(self, root: Optional[Node]):
        self.root = root
        if self.root:
            self.root.calc_world_matrix(glm.mat4())
            self.root.init_human_bones()
            self.root.print_tree()
            self.root.calc_bind_matrix(glm.mat4())
            self.root.calc_world_matrix(glm.mat4())
            self.humanoid_node_map = {node.humanoid_bone: node for node,
                                      _ in self.root.traverse_node_and_parent(only_human_bone=True)}
            self.node_shape_map.clear()
            for node, shape in BoneShape.from_root(self.root, self.gizmo, get_coordinate=get_unitychan_coords).items():
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
                from . import tpose
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

    def sync_gizmo(self):
        for node, shape in self.node_shape_map.items():
            shape.matrix.set(node.world_matrix * glm.mat4(node.local_axis))
