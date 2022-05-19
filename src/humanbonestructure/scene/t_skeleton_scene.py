from typing import Optional, Dict
import glm
from pydear.gizmo.gizmo import Gizmo
from pydear.gizmo.shapes.shape import Shape
from pydear.utils.eventproperty import EventProperty
from pydear.scene.camera import MouseEvent
from pydear.scene.camera import Camera
from ..humanoid.humanoid_skeleton import HumanoidSkeleton
from ..humanoid.pose import Pose
from ..humanoid import blender_coordinate
from ..scene.node import Node
from ..scene.node_drag_handler import NodeDragHandler, sync_gizmo_with_node


class TSkeletonScene:
    def __init__(self, mouse_event: MouseEvent) -> None:
        self.mouse_event = mouse_event
        self.camera = Camera(distance=8, y=-0.8)
        self.camera.bind_mouse_event(self.mouse_event)
        self.gizmo = Gizmo()

        self.skeleton: Optional[HumanoidSkeleton] = None
        self.pose: Optional[Pose] = None

        self.root: Optional[Node] = None
        self.node_shape_map: Dict[Node, Shape] = {}

        self.drag_handler = NodeDragHandler(
            self.gizmo, self.camera, self.node_shape_map, self.raise_pose)
        self.drag_handler.bind_mouse_event_with_gizmo(
            self.mouse_event, self.gizmo)
        self.pose_changed = EventProperty[Pose](Pose('empty'))

        def on_selected(selected: Optional[Shape]):
            if selected:
                position = selected.matrix.value[3].xyz
                self.camera.view.set_gaze(position)
        self.drag_handler.selected += on_selected

    def raise_pose(self):
        assert self.root
        pose = self.root.to_pose()
        self.pose_changed.set(pose)

    def update(self, skeleton: Optional[HumanoidSkeleton], pose: Optional[Pose]):
        if skeleton != self.skeleton:
            # update skeleton
            self.skeleton = skeleton
            if self.skeleton:
                self.root = self.skeleton.to_node()
                self._setup_model()

        if skeleton != self.skeleton or pose != self.pose:
            # update pose
            self._set_pose(pose)

    def _setup_model(self):
        assert self.root
        self.root.calc_world_matrix(glm.mat4())
        self.root.init_human_bones()
        for bone, _ in self.root.traverse_node_and_parent():
            if bone.humanoid_bone.is_enable():
                local_axis = blender_coordinate.BONE_COORDS_MAP[bone.humanoid_bone]
                bone.local_axis = glm.quat(local_axis)
        self.root.calc_world_matrix(glm.mat4())
        self.humanoid_node_map = {node.humanoid_bone: node for node,
                                  _ in self.root.traverse_node_and_parent(only_human_bone=True)}

        from ..gui.bone_shape import BoneShape
        self.node_shape_map.clear()
        for node, shape in BoneShape.from_root(self.root, self.gizmo).items():
            self.node_shape_map[node] = shape

    def _set_pose(self, pose: Optional[Pose]):
        self.pose = pose
        if not self.root or not self.humanoid_node_map:
            return

        self.root.clear_pose()

        # assign pose to node hierarchy
        if pose and pose.bones:
            for bone in pose.bones:
                if bone.humanoid_bone:
                    node = self.humanoid_node_map.get(bone.humanoid_bone)
                    if node:
                        node.pose = bone.transform
                    else:
                        pass
                        # raise RuntimeError()
                else:
                    raise RuntimeError()

        self.root.calc_world_matrix(glm.mat4())

        # sync to gizmo
        self.sync_gizmo()

    def sync_gizmo(self):
        for node, shape in self.node_shape_map.items():
            shape.matrix.set(node.world_matrix * glm.mat4(node.local_axis))

    def render(self, w, h):
        mouse_input = self.mouse_event.last_input
        assert(mouse_input)
        self.camera.projection.resize(w, h)
        self.gizmo.process(self.camera, mouse_input.x, mouse_input.y)
