from typing import Optional, Dict
import glm
from .node import Node
from ..humanoid.bone import Skeleton, Joint, TR, BodyBones, LegBones, FingerBones, ArmBones
from ..humanoid.humanoid_bones import HumanoidBone


def skeleton_from_node(root: Node, node_humanoid_map: Dict[Node, HumanoidBone]) -> Skeleton:
    humanoid_node_map = {v: k for k, v in node_humanoid_map.items()}
    root.calc_world_matrix(glm.mat4())
    # root.print_tree()

    def node_to_joint(node: Node, parent: Optional[Joint] = None) -> Joint:
        if parent:
            m = glm.inverse(parent.world.get_matrix()) * node.world_matrix
            child = Joint(node.name, TR.from_matrix(m),
                          node_humanoid_map[node])
            parent.add_child(child)
            return child
        else:
            return Joint(node.name,
                         TR(node.init_trs.translation,
                            node.init_trs.rotation),
                         node_humanoid_map[node],
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

    hips = node_to_joint(humanoid_node_map[HumanoidBone.hips])
    spine = node_to_joint(humanoid_node_map[HumanoidBone.spine], hips)
    chest = node_to_joint(humanoid_node_map[HumanoidBone.chest], spine)
    neck = node_to_joint(humanoid_node_map[HumanoidBone.neck], chest)
    head = node_to_joint(humanoid_node_map[HumanoidBone.head], neck)
    head_end = create_end(head, lambda pos: pos + glm.vec3(0, 0.2, 0))
    body = BodyBones.create(hips, spine, chest, neck, head, head_end)

    left_upper_leg = node_to_joint(
        humanoid_node_map[HumanoidBone.leftUpperLeg], hips)
    left_lower_leg = node_to_joint(
        humanoid_node_map[HumanoidBone.leftLowerLeg], left_upper_leg)
    left_foot = node_to_joint(
        humanoid_node_map[HumanoidBone.leftFoot], left_lower_leg)
    left_toes = node_to_joint(
        humanoid_node_map[HumanoidBone.leftToes], left_foot)
    left_toes_end = create_end(
        left_toes, lambda pos: pos + glm.vec3(0, 0, 0.1))
    left_leg = LegBones.create(
        left_upper_leg, left_lower_leg, left_foot, left_toes, left_toes_end)

    right_upper_leg = node_to_joint(
        humanoid_node_map[HumanoidBone.rightUpperLeg], hips)
    right_lower_leg = node_to_joint(
        humanoid_node_map[HumanoidBone.rightLowerLeg], right_upper_leg)
    right_foot = node_to_joint(
        humanoid_node_map[HumanoidBone.rightFoot], right_lower_leg)
    right_toes = node_to_joint(
        humanoid_node_map[HumanoidBone.rightToes], right_foot)
    right_toes_end = create_end(
        right_toes, lambda pos: pos+glm.vec3(0, 0, 0.1))
    right_leg = LegBones.create(
        right_upper_leg, right_lower_leg, right_foot, right_toes, right_toes_end)

    #
    left_shoulder = node_to_joint(
        humanoid_node_map[HumanoidBone.leftShoulder], chest)
    left_upper_arm = node_to_joint(
        humanoid_node_map[HumanoidBone.leftUpperArm], left_shoulder)
    left_lower_arm = node_to_joint(
        humanoid_node_map[HumanoidBone.leftLowerArm], left_upper_arm)
    left_hand = node_to_joint(
        humanoid_node_map[HumanoidBone.leftHand], left_lower_arm)

    left_thumb_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftThumbProximal], left_hand)
    left_thumb_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.leftThumbIntermediate], left_thumb_proximal)
    left_thumb_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftThumbDistal], left_thumb_intermediate)
    left_thumb_end = node_to_joint(
        humanoid_node_map[HumanoidBone.leftThumbDistal].children[0], left_thumb_distal)
    left_thumb = FingerBones.create(
        left_thumb_proximal, left_thumb_intermediate, left_thumb_distal, left_thumb_end)

    left_index_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftIndexProximal], left_hand)
    left_index_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.leftIndexIntermediate], left_index_proximal)
    left_index_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftIndexDistal], left_index_intermediate)
    left_index_end = node_to_joint(
        humanoid_node_map[HumanoidBone.leftIndexDistal].children[0], left_index_distal)
    left_index = FingerBones.create(
        left_index_proximal, left_index_intermediate, left_index_distal, left_index_end)

    left_middle_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftMiddleProximal], left_hand)
    left_middle_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.leftMiddleIntermediate], left_middle_proximal)
    left_middle_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftMiddleDistal], left_middle_intermediate)
    left_middle_end = node_to_joint(
        humanoid_node_map[HumanoidBone.leftMiddleDistal].children[0], left_middle_distal)
    left_middle = FingerBones.create(
        left_middle_proximal, left_middle_intermediate, left_middle_distal, left_middle_end)

    left_ring_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftRingProximal], left_hand)
    left_ring_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.leftRingIntermediate], left_ring_proximal)
    left_ring_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftRingDistal], left_ring_intermediate)
    left_ring_end = node_to_joint(
        humanoid_node_map[HumanoidBone.leftRingDistal].children[0], left_ring_distal)
    left_ring = FingerBones.create(
        left_ring_proximal, left_ring_intermediate, left_ring_distal, left_ring_end)

    left_little_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftLittleProximal], left_hand)
    left_little_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.leftLittleIntermediate], left_little_proximal)
    left_little_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.leftLittleDistal], left_little_intermediate)
    left_little_end = node_to_joint(
        humanoid_node_map[HumanoidBone.leftLittleDistal].children[0], left_little_distal)
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
        humanoid_node_map[HumanoidBone.rightShoulder], chest)
    right_upper_arm = node_to_joint(
        humanoid_node_map[HumanoidBone.rightUpperArm], right_shoulder)
    right_lower_arm = node_to_joint(
        humanoid_node_map[HumanoidBone.rightLowerArm], right_upper_arm)
    right_hand = node_to_joint(
        humanoid_node_map[HumanoidBone.rightHand], right_lower_arm)
    right_thumb_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightThumbProximal], right_hand)
    right_thumb_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.rightThumbIntermediate], right_thumb_proximal)
    right_thumb_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightThumbDistal], right_thumb_intermediate)
    right_thumb_end = node_to_joint(
        humanoid_node_map[HumanoidBone.rightThumbDistal].children[0], right_thumb_distal)
    right_thumb = FingerBones.create(
        right_thumb_proximal, right_thumb_intermediate, right_thumb_distal, right_thumb_end)

    right_index_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightIndexProximal], right_hand)
    right_index_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.rightIndexIntermediate], right_index_proximal)
    right_index_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightIndexDistal], right_index_intermediate)
    right_index_end = node_to_joint(
        humanoid_node_map[HumanoidBone.rightIndexDistal].children[0], right_index_distal)
    right_index = FingerBones.create(
        right_index_proximal, right_index_intermediate, right_index_distal, right_index_end)

    right_middle_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightMiddleProximal], right_hand)
    right_middle_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.rightMiddleIntermediate], right_middle_proximal)
    right_middle_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightMiddleDistal], right_middle_intermediate)
    right_middle_end = node_to_joint(
        humanoid_node_map[HumanoidBone.rightMiddleDistal].children[0], right_middle_distal)
    right_middle = FingerBones.create(
        right_middle_proximal, right_middle_intermediate, right_middle_distal, right_middle_end)

    right_ring_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightRingProximal], right_hand)
    right_ring_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.rightRingIntermediate], right_ring_proximal)
    right_ring_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightRingDistal], right_ring_intermediate)
    right_ring_end = node_to_joint(
        humanoid_node_map[HumanoidBone.rightRingDistal].children[0], right_ring_distal)
    right_ring = FingerBones.create(
        right_ring_proximal, right_ring_intermediate, right_ring_distal, right_ring_end)

    right_little_proximal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightLittleProximal], right_hand)
    right_little_intermediate = node_to_joint(
        humanoid_node_map[HumanoidBone.rightLittleIntermediate], right_little_proximal)
    right_little_distal = node_to_joint(
        humanoid_node_map[HumanoidBone.rightLittleDistal], right_little_intermediate)
    right_little_end = node_to_joint(
        humanoid_node_map[HumanoidBone.rightLittleDistal].children[0], right_little_distal)
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

    return Skeleton(body,
                    left_leg, right_leg,
                    left_arm, right_arm
                    )
