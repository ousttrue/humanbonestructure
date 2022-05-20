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
from ..humanoid.bone import Bone, Skeleton, BodyBones, LegBones, FingerBones, ArmBones, Joint, TR
from .unitychan_coords import get_unitychan_coords
from .node import Node
from .bone_shape import BoneShape


class NodeScene:
    def __init__(self, mouse_event: MouseEvent) -> None:
        self.skeleton: Optional[Skeleton] = None

        self.mouse_event = mouse_event
        self.camera = Camera(distance=8, y=-0.8)
        self.camera.bind_mouse_event(self.mouse_event)
        self.gizmo = Gizmo()
        self.bone_shape_map: Dict[Bone, Shape] = {}

        # shape select
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
        self.root.print_tree()

        def node_to_joint(node: Node, parent: Optional[Joint] = None) -> Joint:
            if parent:
                m = glm.inverse(parent.world.get_matrix()) * node.world_matrix
                child = Joint(node.name, TR.from_matrix(m), node.humanoid_bone)
                parent.add_child(child)
                return child
            else:
                return Joint(node.name,
                             TR(node.init_trs.translation,
                                node.init_trs.rotation),
                             node.humanoid_bone,
                             world=TR.from_matrix(node.world_matrix))

        def create_end(parent: Joint, get_pos) -> Joint:
            world_pos = parent.world.translation
            world_end_pos = get_pos(world_pos)
            local_end_pos = glm.inverse(
                parent.world.get_matrix()) * world_end_pos
            end = Joint(f'{parent.name}_end', TR(
                local_end_pos, glm.quat()), HumanoidBone.endSite)
            parent.add_child(end)
            end.calc_world(parent.world)
            return end

        hips = node_to_joint(self.root[HumanoidBone.hips])
        spine = node_to_joint(self.root[HumanoidBone.spine], hips)
        chest = node_to_joint(self.root[HumanoidBone.chest], spine)
        neck = node_to_joint(self.root[HumanoidBone.neck], chest)
        head = node_to_joint(self.root[HumanoidBone.head], neck)
        head_end = create_end(head, lambda pos: pos + glm.vec3(0, 0.2, 0))
        body = BodyBones.create(hips, spine, chest, neck, head, head_end)

        left_upper_leg = node_to_joint(
            self.root[HumanoidBone.leftUpperLeg], hips)
        left_lower_leg = node_to_joint(
            self.root[HumanoidBone.leftLowerLeg], left_upper_leg)
        left_foot = node_to_joint(
            self.root[HumanoidBone.leftFoot], left_lower_leg)
        left_toes = node_to_joint(self.root[HumanoidBone.leftToes], left_foot)
        left_toes_end = create_end(
            left_toes, lambda pos: pos + glm.vec3(0, 0, 0.1))
        left_leg = LegBones.create(
            left_upper_leg, left_lower_leg, left_foot, left_toes, left_toes_end)

        right_upper_leg = node_to_joint(
            self.root[HumanoidBone.rightUpperLeg], hips)
        right_lower_leg = node_to_joint(
            self.root[HumanoidBone.rightLowerLeg], right_upper_leg)
        right_foot = node_to_joint(
            self.root[HumanoidBone.rightFoot], right_lower_leg)
        right_toes = node_to_joint(
            self.root[HumanoidBone.rightToes], right_foot)
        right_toes_end = create_end(
            right_toes, lambda pos: pos+glm.vec3(0, 0, 0.1))
        right_leg = LegBones.create(
            right_upper_leg, right_lower_leg, right_foot, right_toes, right_toes_end)

        #
        left_shoulder = node_to_joint(
            self.root[HumanoidBone.leftShoulder], chest)
        left_upper_arm = node_to_joint(
            self.root[HumanoidBone.leftUpperArm], left_shoulder)
        left_lower_arm = node_to_joint(
            self.root[HumanoidBone.leftLowerArm], left_upper_arm)
        left_hand = node_to_joint(
            self.root[HumanoidBone.leftHand], left_lower_arm)

        left_thumb_proximal = node_to_joint(
            self.root[HumanoidBone.leftThumbProximal], left_hand)
        left_thumb_intermediate = node_to_joint(
            self.root[HumanoidBone.leftThumbIntermediate], left_thumb_proximal)
        left_thumb_distal = node_to_joint(
            self.root[HumanoidBone.leftThumbDistal], left_thumb_intermediate)
        left_thumb_end = node_to_joint(
            self.root[HumanoidBone.leftThumbDistal].children[0], left_thumb_distal)
        left_thumb = FingerBones.create(
            left_thumb_proximal, left_thumb_intermediate, left_thumb_distal, left_thumb_end)

        left_index_proximal = node_to_joint(
            self.root[HumanoidBone.leftIndexProximal], left_hand)
        left_index_intermediate = node_to_joint(
            self.root[HumanoidBone.leftIndexIntermediate], left_index_proximal)
        left_index_distal = node_to_joint(
            self.root[HumanoidBone.leftIndexDistal], left_index_intermediate)
        left_index_end = node_to_joint(
            self.root[HumanoidBone.leftIndexDistal].children[0], left_index_distal)
        left_index = FingerBones.create(
            left_index_proximal, left_index_intermediate, left_index_distal, left_index_end)

        left_middle_proximal = node_to_joint(
            self.root[HumanoidBone.leftMiddleProximal], left_hand)
        left_middle_intermediate = node_to_joint(
            self.root[HumanoidBone.leftMiddleIntermediate], left_middle_proximal)
        left_middle_distal = node_to_joint(
            self.root[HumanoidBone.leftMiddleDistal], left_middle_intermediate)
        left_middle_end = node_to_joint(
            self.root[HumanoidBone.leftMiddleDistal].children[0], left_middle_distal)
        left_middle = FingerBones.create(
            left_middle_proximal, left_middle_intermediate, left_middle_distal, left_middle_end)

        left_ring_proximal = node_to_joint(
            self.root[HumanoidBone.leftRingProximal], left_hand)
        left_ring_intermediate = node_to_joint(
            self.root[HumanoidBone.leftRingIntermediate], left_ring_proximal)
        left_ring_distal = node_to_joint(
            self.root[HumanoidBone.leftRingDistal], left_ring_intermediate)
        left_ring_end = node_to_joint(
            self.root[HumanoidBone.leftRingDistal].children[0], left_ring_distal)
        left_ring = FingerBones.create(
            left_ring_proximal, left_ring_intermediate, left_ring_distal, left_ring_end)

        left_little_proximal = node_to_joint(
            self.root[HumanoidBone.leftLittleProximal], left_hand)
        left_little_intermediate = node_to_joint(
            self.root[HumanoidBone.leftLittleIntermediate], left_little_proximal)
        left_little_distal = node_to_joint(
            self.root[HumanoidBone.leftLittleDistal], left_little_intermediate)
        left_little_end = node_to_joint(
            self.root[HumanoidBone.leftLittleDistal].children[0], left_little_distal)
        left_little = FingerBones.create(
            left_little_proximal, left_little_intermediate, left_little_distal, left_little_end)

        left_arm = ArmBones.create(
            left_shoulder, left_upper_arm, left_lower_arm, left_hand,
            thumb=left_thumb,
            index=left_index,
            middle=left_middle,
            ring=left_ring,
            little=left_little
        )

        #
        right_shoulder = node_to_joint(
            self.root[HumanoidBone.rightShoulder], chest)
        right_upper_arm = node_to_joint(
            self.root[HumanoidBone.rightUpperArm], right_shoulder)
        right_lower_arm = node_to_joint(
            self.root[HumanoidBone.rightLowerArm], right_upper_arm)
        right_hand = node_to_joint(
            self.root[HumanoidBone.rightHand], right_lower_arm)
        right_thumb_proximal = node_to_joint(
            self.root[HumanoidBone.rightThumbProximal], right_hand)
        right_thumb_intermediate = node_to_joint(
            self.root[HumanoidBone.rightThumbIntermediate], right_thumb_proximal)
        right_thumb_distal = node_to_joint(
            self.root[HumanoidBone.rightThumbDistal], right_thumb_intermediate)
        right_thumb_end = node_to_joint(
            self.root[HumanoidBone.rightThumbDistal].children[0], right_thumb_distal)
        right_thumb = FingerBones.create(
            right_thumb_proximal, right_thumb_intermediate, right_thumb_distal, right_thumb_end)

        right_index_proximal = node_to_joint(
            self.root[HumanoidBone.rightIndexProximal], right_hand)
        right_index_intermediate = node_to_joint(
            self.root[HumanoidBone.rightIndexIntermediate], right_index_proximal)
        right_index_distal = node_to_joint(
            self.root[HumanoidBone.rightIndexDistal], right_index_intermediate)
        right_index_end = node_to_joint(
            self.root[HumanoidBone.rightIndexDistal].children[0], right_index_distal)
        right_index = FingerBones.create(
            right_index_proximal, right_index_intermediate, right_index_distal, right_index_end)

        right_middle_proximal = node_to_joint(
            self.root[HumanoidBone.rightMiddleProximal], right_hand)
        right_middle_intermediate = node_to_joint(
            self.root[HumanoidBone.rightMiddleIntermediate], right_middle_proximal)
        right_middle_distal = node_to_joint(
            self.root[HumanoidBone.rightMiddleDistal], right_middle_intermediate)
        right_middle_end = node_to_joint(
            self.root[HumanoidBone.rightMiddleDistal].children[0], right_middle_distal)
        right_middle = FingerBones.create(
            right_middle_proximal, right_middle_intermediate, right_middle_distal, right_middle_end)

        right_ring_proximal = node_to_joint(
            self.root[HumanoidBone.rightRingProximal], right_hand)
        right_ring_intermediate = node_to_joint(
            self.root[HumanoidBone.rightRingIntermediate], right_ring_proximal)
        right_ring_distal = node_to_joint(
            self.root[HumanoidBone.rightRingDistal], right_ring_intermediate)
        right_ring_end = node_to_joint(
            self.root[HumanoidBone.rightRingDistal].children[0], right_ring_distal)
        right_ring = FingerBones.create(
            right_ring_proximal, right_ring_intermediate, right_ring_distal, right_ring_end)

        right_little_proximal = node_to_joint(
            self.root[HumanoidBone.rightLittleProximal], right_hand)
        right_little_intermediate = node_to_joint(
            self.root[HumanoidBone.rightLittleIntermediate], right_little_proximal)
        right_little_distal = node_to_joint(
            self.root[HumanoidBone.rightLittleDistal], right_little_intermediate)
        right_little_end = node_to_joint(
            self.root[HumanoidBone.rightLittleDistal].children[0], right_little_distal)
        right_little = FingerBones.create(
            right_little_proximal, right_little_intermediate, right_little_distal, right_little_end)

        right_arm = ArmBones.create(
            right_shoulder, right_upper_arm, right_lower_arm, right_hand,
            thumb=right_thumb,
            index=right_index,
            middle=right_middle,
            ring=right_ring,
            little=right_little
        )

        self.skeleton = Skeleton(body,
                                 left_leg, right_leg,
                                 left_arm, right_arm
                                 )

        self.bone_shape_map = BoneShape.from_skeleton(
            self.skeleton, self.gizmo)

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
        if not self.skeleton:
            return

        self.skeleton.calc_world_matrix()
        for bone, shape in self.bone_shape_map.items():
            shape.matrix.set(bone.head.world.get_matrix())
