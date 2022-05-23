from typing import Optional, Tuple, Dict
import glm
from pydear.utils.mouse_event import MouseEvent
from pydear.scene.camera import Camera, ArcBall, ScreenShift
from pydear.gizmo.gizmo import Gizmo
from pydear.gizmo.gizmo_select_handler import GizmoSelectHandler
from pydear.gizmo.shapes.shape import Shape
from ..humanoid.pose import Pose
from ..humanoid.bone import Bone, Skeleton
from .unitychan_coords import get_unitychan_coords
from .node import Node
from .bone_shape import BoneShape


class NodeScene:
    def __init__(self, mouse_event: MouseEvent) -> None:
        self.skeleton: Optional[Skeleton] = None

        self.mouse_event = mouse_event
        self.camera = Camera(distance=8, y=-0.8)
        self.arc = ArcBall(self.camera.view, self.camera.projection)
        self.mouse_event.bind_right_drag(self.arc)
        self.shift = ScreenShift(self.camera.view, self.camera.projection)
        self.mouse_event.bind_middle_drag(self.shift)
        self.mouse_event.wheel += [self.shift.wheel]

        self.gizmo = None
        self.bone_shape_map: Dict[Bone, Shape] = {}

        # shape select
        # self.drag_handler = GizmoSelectHandler(self.gizmo)
        # self.mouse_event.bind_left_drag(self.drag_handler)

        # def on_selected(selected: Optional[Shape]):
        #     if selected:
        #         position = selected.matrix.value[3].xyz
        #         self.camera.view.set_gaze(position)
        # self.drag_handler.selected += on_selected
        self.cancel_axis = False

    def render(self, w: int, h: int):
        if not self.gizmo:
            return
        mouse_input = self.mouse_event.last_input
        assert(mouse_input)
        self.camera.projection.resize(w, h)
        self.gizmo.process(self.camera, mouse_input.x, mouse_input.y)

    def update(self, skeleton: Optional[Skeleton], pose: Optional[Pose], cancel_axis: bool = False):
        if cancel_axis != self.cancel_axis:
            self.cancel_axis = cancel_axis
            # clear
            self.skeleton = None


        if self.skeleton != skeleton:
            self.skeleton = skeleton
            if self.skeleton:
                if self.cancel_axis:
                    self.skeleton.cancel_axis()
                else:
                    self.skeleton.clear_axis()
                self.gizmo = Gizmo()
                self.bone_shape_map = BoneShape.from_skeleton(
                    self.skeleton, self.gizmo)

        # if not self.root:
        #     return
        # if not self.humanoid_node_map:
        #     return

        # if self.pose_conv == (pose, convert):
        #     return
        # self.pose_conv = (pose, convert)

        # self.root.clear_pose()

        # if convert:
        #     if not self.tpose_delta_map:
        #         # make tpose for pose conversion
        #         from . import tpose
        #         tpose.make_tpose(self.root)
        #         self.tpose_delta_map: Dict[HumanoidBone, glm.quat] = {node.humanoid_bone: node.pose.rotation if node.pose else glm.quat(
        #         ) for node, _ in self.root.traverse_node_and_parent(only_human_bone=True)}
        #         tpose.local_axis_fit_world(self.root)
        #         self.root.clear_pose()
        # else:
        #     self.tpose_delta_map.clear()
        #     self.root.clear_local_axis()

        # # assign pose to node hierarchy
        # if pose and pose.bones:
        #     for bone in pose.bones:
        #         if bone.humanoid_bone:
        #             node = self.humanoid_node_map.get(bone.humanoid_bone)
        #             if node:
        #                 if convert:
        #                     d = self.tpose_delta_map.get(
        #                         node.humanoid_bone, glm.quat())
        #                     a = node.local_axis
        #                     node.pose = Transform.from_rotation(
        #                         glm.inverse(d) * a * bone.transform.rotation * glm.inverse(a))
        #                 else:
        #                     node.pose = bone.transform
        #             else:
        #                 pass
        #                 # raise RuntimeError()
        #         else:
        #             raise RuntimeError()

        # self.root.calc_world_matrix(glm.mat4())

        # # sync to gizmo
        # for node, shape in self.node_shape_map.items():
        #     shape.matrix.set(node.world_matrix)

    def sync_gizmo(self):
        if not self.skeleton:
            return

        self.skeleton.calc_world_matrix()
        for bone, shape in self.bone_shape_map.items():
            shape.matrix.set(bone.head.world.get_matrix())
