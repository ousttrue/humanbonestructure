from typing import NamedTuple, Dict, TypeAlias, Optional
import glm
from ..scene.node import Node
from .humanoid_bones import HumanoidBone, LeftRight, Fingers, UP
from . import tpose
from .transform import Transform

NodeMap: TypeAlias = Dict[HumanoidBone, Node]


class HumanoidSkeletonTrunk(NamedTuple):
    position: glm.vec3
    hips: float
    spine: float
    chest: float
    neck: float
    head: float

    @staticmethod
    def from_node_map(node_map: NodeMap) -> Optional['HumanoidSkeletonTrunk']:
        hips = node_map[HumanoidBone.hips].world_matrix[3].xyz
        spine = node_map[HumanoidBone.spine].world_matrix[3].xyz
        chest = node_map[HumanoidBone.chest].world_matrix[3].xyz
        neck = node_map[HumanoidBone.neck].world_matrix[3].xyz
        head = node_map[HumanoidBone.head].world_matrix[3].xyz
        head_end = node_map[HumanoidBone.head].humanoid_tail
        assert(head_end)

        return HumanoidSkeletonTrunk(hips,
                                     glm.length(spine-hips),
                                     glm.length(chest-spine),
                                     glm.length(neck-chest),
                                     glm.length(head-neck),
                                     glm.length(
                                         head_end.world_matrix[3].xyz-head),
                                     )

    def to_node(self) -> Node:
        d = glm.vec3(0, 1, 0)
        return Node('hips', Transform.from_translation(self.position), HumanoidBone.hips, children=[
            Node('spine', Transform.from_translation(d*self.hips), HumanoidBone.spine, children=[
                Node('chest', Transform.from_translation(d*self.chest), HumanoidBone.chest, children=[
                    Node('neck', Transform.from_translation(d*self.chest), HumanoidBone.neck, children=[
                        Node('head', Transform.from_translation(d*self.neck), HumanoidBone.head, children=[
                            Node('head_end', Transform.from_translation(
                                d*self.head), HumanoidBone.endSite)
                        ])
                    ])
                ])
            ])
        ])


class HumanoidSkeletonLeftArm(NamedTuple):
    position: glm.vec3
    shoulder: float
    upper_arm: float
    lower_arm: float
    hand: float

    @staticmethod
    def from_node_map(node_map: NodeMap) -> Optional['HumanoidSkeletonLeftArm']:
        chest = node_map.get(HumanoidBone.chest)
        chest_position = chest.world_matrix[3].xyz if chest else glm.vec3(
            0)
        shoulder = node_map[HumanoidBone.leftShoulder].world_matrix[3].xyz
        upper = node_map[HumanoidBone.leftUpperArm].world_matrix[3].xyz
        lower = node_map[HumanoidBone.leftLowerArm].world_matrix[3].xyz
        hand = node_map[HumanoidBone.leftHand].world_matrix[3].xyz
        hand_end = node_map.get(HumanoidBone.leftMiddleProximal)
        if not hand_end:
            hand_end = node_map[HumanoidBone.leftHand].humanoid_tail
            assert(hand_end)
        return HumanoidSkeletonLeftArm(shoulder-chest_position,
                                       glm.length(upper-shoulder),
                                       glm.length(lower-upper),
                                       glm.length(hand-lower),
                                       glm.length(
                                           hand_end.world_matrix[3].xyz - hand),
                                       )

    def to_node(self) -> Node:
        d = glm.vec3(1, 0, 0)
        return Node('leftSoulder', Transform.from_translation(self.position), HumanoidBone.leftShoulder, children=[
            Node('leftUpperArm', Transform.from_translation(d*self.shoulder), HumanoidBone.leftUpperArm, children=[
                Node('leftLowerArm', Transform.from_translation(d*self.upper_arm), HumanoidBone.leftLowerArm, children=[
                    Node('leftHand', Transform.from_translation(d*self.lower_arm), HumanoidBone.leftHand, children=[
                        Node('leftHandEnd', Transform.from_translation(
                            d*self.hand), HumanoidBone.endSite)
                    ])
                ])
            ])
        ])


class HumanoidSkeletonRightArm(NamedTuple):
    position: glm.vec3
    shoulder: float
    upper_arm: float
    lower_arm: float
    hand: float

    @staticmethod
    def from_node_map(node_map: NodeMap) -> Optional['HumanoidSkeletonRightArm']:
        chest = node_map.get(HumanoidBone.chest)
        chest_position = chest.world_matrix[3].xyz if chest else glm.vec3(
            0)
        shoulder = node_map[HumanoidBone.rightShoulder].world_matrix[3].xyz
        upper = node_map[HumanoidBone.rightUpperArm].world_matrix[3].xyz
        lower = node_map[HumanoidBone.rightLowerArm].world_matrix[3].xyz
        hand = node_map[HumanoidBone.rightHand].world_matrix[3].xyz
        hand_end = node_map.get(HumanoidBone.rightMiddleProximal)
        if not hand_end:
            hand_end = node_map[HumanoidBone.rightHand].humanoid_tail
            assert(hand_end)
        return HumanoidSkeletonRightArm(shoulder-chest_position,
                                        glm.length(upper-shoulder),
                                        glm.length(lower-upper),
                                        glm.length(hand-lower),
                                        glm.length(
                                            hand_end.world_matrix[3].xyz - hand),
                                        )

    def to_node(self) -> Node:
        d = glm.vec3(-1, 0, 0)
        return Node('rightSoulder', Transform.from_translation(self.position), HumanoidBone.rightShoulder, children=[
            Node('rightUpperArm', Transform.from_translation(d*self.shoulder), HumanoidBone.rightUpperArm, children=[
                Node('rightLowerArm', Transform.from_translation(d*self.upper_arm), HumanoidBone.rightLowerArm, children=[
                    Node('rightHand', Transform.from_translation(d*self.lower_arm), HumanoidBone.rightHand, children=[
                        Node('rightHandEnd', Transform.from_translation(
                            d*self.hand), HumanoidBone.endSite)
                    ])
                ])
            ])
        ])


class HumanoidSkeletonLeftLeg(NamedTuple):
    position: glm.vec3
    upper_leg: float
    lower_leg: float
    foot: float

    @staticmethod
    def from_node_map(node_map: NodeMap) -> Optional['HumanoidSkeletonLeftLeg']:
        hips = node_map[HumanoidBone.hips].world_matrix[3].xyz
        upper = node_map[HumanoidBone.leftUpperLeg].world_matrix[3].xyz
        lower = node_map[HumanoidBone.leftLowerLeg].world_matrix[3].xyz
        foot = node_map[HumanoidBone.leftFoot].world_matrix[3].xyz
        foot_end = node_map[HumanoidBone.leftFoot].humanoid_tail
        assert(foot_end)
        return HumanoidSkeletonLeftLeg(upper-hips,
                                       glm.length(lower-upper),
                                       glm.length(foot-lower),
                                       glm.length(
                                           foot_end.world_matrix[3].xyz-foot))

    def to_node(self) -> Node:
        d = glm.vec3(0, -1, 0)
        return Node('leftUpperLeg', Transform.from_translation(self.position), HumanoidBone.leftUpperLeg, children=[
            Node('leftLowerLeg', Transform.from_translation(d*self.upper_leg), HumanoidBone.leftLowerLeg, children=[
                Node('leftFoot', Transform.from_translation(d*self.lower_leg), HumanoidBone.leftFoot, children=[
                    Node('leftHeal', Transform.from_translation(
                        d*self.foot), HumanoidBone.endSite)
                ])
            ])
        ])


class HumanoidSkeletonRightLeg(NamedTuple):
    position: glm.vec3
    upper_leg: float
    lower_leg: float
    foot: float

    @staticmethod
    def from_node_map(node_map: NodeMap) -> Optional['HumanoidSkeletonRightLeg']:
        hips = node_map[HumanoidBone.hips].world_matrix[3].xyz
        upper = node_map[HumanoidBone.rightUpperLeg].world_matrix[3].xyz
        lower = node_map[HumanoidBone.rightLowerLeg].world_matrix[3].xyz
        foot = node_map[HumanoidBone.rightFoot].world_matrix[3].xyz
        foot_end = node_map[HumanoidBone.rightFoot].humanoid_tail
        assert(foot_end)
        return HumanoidSkeletonRightLeg(upper-hips,
                                        glm.length(lower-upper),
                                        glm.length(foot-lower),
                                        glm.length(
                                            foot_end.world_matrix[3].xyz-foot))

    def to_node(self) -> Node:
        d = glm.vec3(0, -1, 0)
        return Node('rightUpperLeg', Transform.from_translation(self.position), HumanoidBone.rightUpperLeg, children=[
            Node('rightLowerLeg', Transform.from_translation(d*self.upper_leg), HumanoidBone.rightLowerLeg, children=[
                Node('rightFoot', Transform.from_translation(d*self.lower_leg), HumanoidBone.rightFoot, children=[
                    Node('rightHeal', Transform.from_translation(
                        d*self.foot), HumanoidBone.endSite)
                ])
            ])
        ])


class HumanoidSkeletonLeftToes(NamedTuple):
    position: glm.vec3
    toes: float

    @ staticmethod
    def from_node_map(node_map: NodeMap) -> Optional['HumanoidSkeletonLeftToes']:
        pass

    def to_node(self) -> Node:
        d = glm.vec3(0, 0, 1)
        return Node('leftToes', Transform.from_translation(self.position), HumanoidBone.leftToes, children=[
            Node('endsite', Transform.from_translation(
                d*self.toes), HumanoidBone.endSite)
        ])


class HumanoidSkeletonRightToes(NamedTuple):
    position: glm.vec3
    toes: float

    @ staticmethod
    def from_node_map(node_map: NodeMap) -> Optional['HumanoidSkeletonRightToes']:
        pass

    def to_node(self) -> Node:
        d = glm.vec3(0, 0, 1)
        return Node('rightToes', Transform.from_translation(self.position), HumanoidBone.rightToes, children=[
            Node('endsite', Transform.from_translation(
                d*self.toes), HumanoidBone.endSite)
        ])


class HumanoidSkeletonFinger(NamedTuple):
    position: glm.vec3
    finger1: float
    finger2: float
    finger3: float

    @ staticmethod
    def from_node_map(node_map: NodeMap, left_right: LeftRight, fingers: Fingers) -> Optional['HumanoidSkeletonFinger']:
        pass


class HumanoidSkeletonFingers(NamedTuple):
    thumbnail: HumanoidSkeletonFinger
    index: HumanoidSkeletonFinger
    middle: HumanoidSkeletonFinger
    ring: HumanoidSkeletonFinger
    little: HumanoidSkeletonFinger

    @ staticmethod
    def from_node_map(node_map: NodeMap, left_right: LeftRight) -> Optional['HumanoidSkeletonFingers']:
        pass


PARTS_MAP = {
    'trunk': HumanoidSkeletonTrunk,
    'left_leg': HumanoidSkeletonLeftLeg,
    'right_leg': HumanoidSkeletonRightLeg,
    'left_arm': HumanoidSkeletonLeftArm,
    'right_arm': HumanoidSkeletonRightArm,
}


def to_dict(node_map: NodeMap) -> dict:
    parts_map = {}

    for k, t in PARTS_MAP.items():
        if value := t.from_node_map(node_map):
            parts_map[k] = value

    return parts_map


class HumanoidSkeleton:

    def __init__(self,
                 *,
                 trunk: HumanoidSkeletonTrunk,
                 left_leg: HumanoidSkeletonLeftLeg,
                 right_leg: HumanoidSkeletonRightLeg,
                 left_arm: HumanoidSkeletonLeftArm,
                 right_arm: HumanoidSkeletonRightArm,
                 #
                 left_toes: Optional[HumanoidSkeletonLeftToes] = None,
                 right_toes: Optional[HumanoidSkeletonRightToes] = None,
                 #
                 left_fingers: Optional[HumanoidSkeletonFingers] = None,
                 right_fingers: Optional[HumanoidSkeletonFingers] = None
                 ) -> None:
        # Physique
        self.trunk = trunk
        self.left_leg = left_leg
        self.right_leg = right_leg
        self.left_arm = left_arm
        self.right_arm = right_arm
        self.left_toes = left_toes
        self.right_toes = right_toes
        self.left_fingers = left_fingers
        self.right_fingers = right_fingers

        # InitialPose
        self.init_pose: Dict[HumanoidBone, glm.quat] = {}

    @ staticmethod
    def from_node(root: Node, *, is_inverted_pelvis=False) -> 'HumanoidSkeleton':
        copy = root.copy_tree()
        tpose.make_tpose(copy, is_inverted_pelvis=is_inverted_pelvis)
        copy.init_human_bones()
        copy.calc_world_matrix(glm.mat4())
        node_map: NodeMap = {node.humanoid_bone: node for node,
                             _ in copy.traverse_node_and_parent(only_human_bone=True)}

        kw = to_dict(node_map)

        return HumanoidSkeleton(**kw)

    def to_node(self) -> Node:
        root = Node('__root__', Transform.identity())
        hips = self.trunk.to_node()
        #
        left_leg = self.left_leg.to_node()
        hips.add_child(left_leg)
        right_leg = self.right_leg.to_node()
        hips.add_child(right_leg)
        #
        chest = hips.find_humanoid_bone(HumanoidBone.chest)
        assert(chest)
        left_arm = self.left_arm.to_node()
        chest.add_child(left_arm)
        right_arm = self.right_arm.to_node()
        chest.add_child(right_arm)
        #
        root.add_child(hips)

        if self.left_toes:
            left_toes = self.left_toes.to_node()
            root[HumanoidBone.leftFoot].add_child(left_toes)
        if self.right_toes:
            right_toes = self.right_toes.to_node()
            root[HumanoidBone.rightFoot].add_child(right_toes)

        return root
