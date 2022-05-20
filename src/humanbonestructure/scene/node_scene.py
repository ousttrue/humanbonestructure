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
        if not self.root:
            return

        self.root.calc_world_matrix(glm.mat4())
        from ..humanoid.bone import Skeleton, BodyBones, LegBones, ArmBones, Joint, TR

        def get_joint(node: Node) -> Joint:
            return Joint(node.name,
                         TR(node.init_trs.translation, node.init_trs.rotation),
                         node.humanoid_bone,
                         world=TR.from_matrix(node.world_matrix))
        hips = get_joint(self.root[HumanoidBone.hips])
        spine = get_joint(self.root[HumanoidBone.spine])
        chest = get_joint(self.root[HumanoidBone.chest])
        neck = get_joint(self.root[HumanoidBone.neck])
        head_node = self.root[HumanoidBone.head]
        head = get_joint(head_node)
        head_pos = head_node.world_matrix[3].xyz
        head_end = head_pos + glm.vec3(0, 0.2, 0)
        head_local_end = glm.inverse(head_node.world_matrix) * head_end
        head_end_node = Node(
            'head_end', Transform.from_translation(head_local_end), HumanoidBone.endSite)
        head_node.add_child(head_end_node)
        head_end_node.calc_world_matrix(head_node.world_matrix)
        head_end = get_joint(head_end_node)
        body = BodyBones.create(hips, spine, chest, neck, head, head_end)

        left_upper_leg = get_joint(self.root[HumanoidBone.leftUpperLeg])
        left_lower_leg = get_joint(self.root[HumanoidBone.leftLowerLeg])
        left_foot_node = self.root[HumanoidBone.leftFoot]
        left_foot = get_joint(left_foot_node)
        left_foot_pos = left_foot_node.world_matrix[3].xyz
        left_foot_end = glm.vec3(left_foot_pos.x, 0, left_foot_pos.z)
        left_foot_local_end = glm.inverse(
            left_foot_node.world_matrix) * left_foot_end
        left_heel_node = Node(
            'left_heel', Transform.from_translation(left_foot_local_end), HumanoidBone.endSite)
        left_foot_node.add_child(left_heel_node)
        left_heel_node.calc_bind_matrix(left_foot_node.world_matrix)
        left_heel = get_joint(left_heel_node)
        left_leg = LegBones.create(
            left_upper_leg, left_lower_leg, left_foot, left_heel)

        right_upper_leg = get_joint(self.root[HumanoidBone.rightUpperLeg])
        right_lower_leg = get_joint(self.root[HumanoidBone.rightLowerLeg])
        right_foot_node = self.root[HumanoidBone.rightFoot]
        right_foot = get_joint(right_foot_node)
        right_foot_pos = right_foot_node.world_matrix[3].xyz
        right_foot_end = glm.vec3(right_foot_pos.x, 0, right_foot_pos.z)
        right_foot_local_end = glm.inverse(
            right_foot_node.world_matrix) * right_foot_end
        right_heel_node = Node(
            'right_heel', Transform.from_translation(right_foot_local_end), HumanoidBone.endSite)
        right_foot_node.add_child(right_heel_node)
        right_heel_node.calc_bind_matrix(right_foot_node.world_matrix)
        right_heel = get_joint(right_heel_node)
        right_leg = LegBones.create(
            right_upper_leg, right_lower_leg, right_foot, right_heel)

        left_shoulder = get_joint(self.root[HumanoidBone.leftShoulder])
        left_upper_arm = get_joint(self.root[HumanoidBone.leftUpperArm])
        left_lower_arm = get_joint(self.root[HumanoidBone.leftLowerArm])
        left_middle_proximal = get_joint(
            self.root[HumanoidBone.leftMiddleProximal])
        left_arm = ArmBones.create(
            left_shoulder, left_upper_arm, left_lower_arm, left_middle_proximal)

        right_shoulder = get_joint(self.root[HumanoidBone.rightShoulder])
        right_upper_arm = get_joint(self.root[HumanoidBone.rightUpperArm])
        right_lower_arm = get_joint(self.root[HumanoidBone.rightLowerArm])
        right_middle_proximal = get_joint(
            self.root[HumanoidBone.rightMiddleProximal])
        right_arm = ArmBones.create(
            right_shoulder, right_upper_arm, right_lower_arm, right_middle_proximal)

        self.skeleton = Skeleton(body,
                                 left_leg, right_leg,
                                 left_arm, right_arm)
        BoneShape.from_skeleton(self.skeleton, self.gizmo)

        # self.root.init_human_bones()
        # self.root.print_tree()
        # # Clear node rotation and set local_axis
        # self.root.calc_world_matrix(glm.mat4())
        # world_map = {}
        # for node, _ in self.root.traverse_node_and_parent():
        #     world_map[node] = node.world_matrix
        # for node, parent in self.root.traverse_node_and_parent():
        #     parent_pos = world_map[parent][3].xyz if parent else glm.vec3(0, 0, 0)
        #     node.init_trs = Transform.from_translation(world_map[node][3].xyz-parent_pos)
        #     node.local_axis = glm.quat(world_map[node])
        # # setup
        # self.root.calc_world_matrix(glm.mat4())
        # self.root.init_human_bones()
        # self.root.calc_bind_matrix(glm.mat4())
        # self.root.calc_world_matrix(glm.mat4())
        # self.humanoid_node_map = {node.humanoid_bone: node for node,
        #                             _ in self.root.traverse_node_and_parent(only_human_bone=True)}
        # self.node_shape_map.clear()
        # for node, shape in BoneShape.from_root(self.root, self.gizmo).items():
        #     self.node_shape_map[node] = shape

    def set_pose(self, pose: Optional[Pose], convert: bool):
        if not self.root:
            return
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
        for node, shape in self.node_shape_map.items():
            shape.matrix.set(node.world_matrix * glm.mat4(node.local_axis))
