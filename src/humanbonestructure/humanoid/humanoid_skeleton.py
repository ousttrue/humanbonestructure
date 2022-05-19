from typing import NamedTuple, Dict, TypeAlias, Optional
import glm
from ..scene.node import Node
from .humanoid_bones import HumanoidBone, BoneBase, BoneFlags
from . import tpose
from .transform import Transform
from .humanoid_hand import HumanoidHand, HumanoidFinger

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

    @staticmethod
    def from_node_map(node_map: NodeMap) -> Optional['HumanoidSkeletonLeftArm']:
        chest = node_map.get(HumanoidBone.chest)
        chest_position = chest.world_matrix[3].xyz if chest else glm.vec3(
            0)
        shoulder = node_map[HumanoidBone.leftShoulder].world_matrix[3].xyz
        upper = node_map[HumanoidBone.leftUpperArm].world_matrix[3].xyz
        lower = node_map[HumanoidBone.leftLowerArm].world_matrix[3].xyz
        hand = node_map[HumanoidBone.leftHand].world_matrix[3].xyz
        return HumanoidSkeletonLeftArm(shoulder-chest_position,
                                       glm.length(upper-shoulder),
                                       glm.length(lower-upper),
                                       glm.length(hand-lower))

    def to_node(self) -> Node:
        d = glm.vec3(1, 0, 0)
        return Node('leftSoulder', Transform.from_translation(self.position), HumanoidBone.leftShoulder, children=[
            Node('leftUpperArm', Transform.from_translation(d*self.shoulder), HumanoidBone.leftUpperArm, children=[
                Node('leftLowerArm', Transform.from_translation(d*self.upper_arm), HumanoidBone.leftLowerArm, children=[
                    Node('leftHand', Transform.from_translation(d*self.lower_arm), HumanoidBone.leftHand, children=[
                    ])
                ])
            ])
        ])


class HumanoidSkeletonRightArm(NamedTuple):
    position: glm.vec3
    shoulder: float
    upper_arm: float
    lower_arm: float

    @staticmethod
    def from_node_map(node_map: NodeMap) -> Optional['HumanoidSkeletonRightArm']:
        chest = node_map.get(HumanoidBone.chest)
        chest_position = chest.world_matrix[3].xyz if chest else glm.vec3(
            0)
        shoulder = node_map[HumanoidBone.rightShoulder].world_matrix[3].xyz
        upper = node_map[HumanoidBone.rightUpperArm].world_matrix[3].xyz
        lower = node_map[HumanoidBone.rightLowerArm].world_matrix[3].xyz
        hand = node_map[HumanoidBone.rightHand].world_matrix[3].xyz
        return HumanoidSkeletonRightArm(shoulder-chest_position,
                                        glm.length(upper-shoulder),
                                        glm.length(lower-upper),
                                        glm.length(hand-lower)
                                        )

    def to_node(self) -> Node:
        d = glm.vec3(-1, 0, 0)
        return Node('rightSoulder', Transform.from_translation(self.position), HumanoidBone.rightShoulder, children=[
            Node('rightUpperArm', Transform.from_translation(d*self.shoulder), HumanoidBone.rightUpperArm, children=[
                Node('rightLowerArm', Transform.from_translation(d*self.upper_arm), HumanoidBone.rightLowerArm, children=[
                    Node('rightHand', Transform.from_translation(d*self.lower_arm), HumanoidBone.rightHand, children=[
                    ])
                ])
            ])
        ])


class HumanoidSkeletonLeg(NamedTuple):
    left_right: BoneFlags
    position: glm.vec3
    upper_leg: float
    lower_leg: float
    foot: float

    @staticmethod
    def from_node_map(node_map: NodeMap, left_right: BoneFlags) -> Optional['HumanoidSkeletonLeg']:
        hips = node_map[HumanoidBone.hips].world_matrix[3].xyz
        match left_right:
            case BoneFlags.Left:
                upper = node_map[HumanoidBone.leftUpperLeg].world_matrix[3].xyz
                lower = node_map[HumanoidBone.leftLowerLeg].world_matrix[3].xyz
                foot = node_map[HumanoidBone.leftFoot].world_matrix[3].xyz
                foot_end = node_map[HumanoidBone.leftFoot].humanoid_tail
            case BoneFlags.Right:
                upper = node_map[HumanoidBone.rightUpperLeg].world_matrix[3].xyz
                lower = node_map[HumanoidBone.rightLowerLeg].world_matrix[3].xyz
                foot = node_map[HumanoidBone.rightFoot].world_matrix[3].xyz
                foot_end = node_map[HumanoidBone.rightFoot].humanoid_tail
            case _:
                raise RuntimeError()
        assert(foot_end)
        return HumanoidSkeletonLeg(left_right, upper-hips,
                                   glm.length(lower-upper),
                                   glm.length(foot-lower),
                                   glm.length(
                                       foot_end.world_matrix[3].xyz-foot))

    def to_node(self) -> Node:
        d = glm.vec3(0, -1, 0)
        match self.left_right:
            case BoneFlags.Left:
                prefix = 'left'
            case BoneFlags.Right:
                prefix = 'right'
            case _:
                raise RuntimeError(f"Neither left or right: {self.left_right}")

        def bone(base: BoneBase) -> HumanoidBone:
            return HumanoidBone.baseflag(base, self.left_right)

        return Node(f'{prefix}UpperLeg', Transform.from_translation(self.position), bone(BoneBase.upperLeg), children=[
            Node(f'{prefix}LowerLeg', Transform.from_translation(d*self.upper_leg), bone(BoneBase.lowerLeg), children=[
                Node(f'{prefix}Foot', Transform.from_translation(d*self.lower_leg), bone(BoneBase.foot), children=[
                    Node(f'{prefix}Heal', Transform.from_translation(
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


PARTS_MAP = {
    'trunk': HumanoidSkeletonTrunk,
    'left_leg': HumanoidSkeletonLeg,
    'right_leg': HumanoidSkeletonLeg,
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
                 left_leg: HumanoidSkeletonLeg,
                 right_leg: HumanoidSkeletonLeg,
                 left_arm: HumanoidSkeletonLeftArm,
                 right_arm: HumanoidSkeletonRightArm,
                 left_hand: HumanoidHand,
                 right_hand: HumanoidHand,
                 #
                 left_toes: Optional[HumanoidSkeletonLeftToes] = None,
                 right_toes: Optional[HumanoidSkeletonRightToes] = None,
                 #
                 ) -> None:
        # Physique
        self.trunk = trunk
        self.left_leg = left_leg
        self.right_leg = right_leg
        self.left_arm = left_arm
        self.right_arm = right_arm
        self.left_hand = left_hand
        self.right_hand = right_hand
        self.left_toes = left_toes
        self.right_toes = right_toes

        # InitialPose
        self.init_pose: Dict[HumanoidBone, glm.quat] = {}

    @staticmethod
    def create_default() -> 'HumanoidSkeleton':
        trunk = HumanoidSkeletonTrunk(glm.vec3(0, 0.85, 0),
                                      0.1, 0.1, 0.2, 0.1, 0.2)
        left_leg = HumanoidSkeletonLeg(BoneFlags.Left, glm.vec3(0.1, 0, 0),
                                           0.4, 0.35, 0.08)
        right_leg = HumanoidSkeletonLeg(BoneFlags.Right, glm.vec3(-0.1, 0, 0),
                                             0.4, 0.35, 0.08)
        left_arm = HumanoidSkeletonLeftArm(glm.vec3(0.1, 0.2, 0),
                                           0.1, 0.3, 0.3)
        right_arm = HumanoidSkeletonRightArm(glm.vec3(-0.1, 0.2, 0),
                                             0.1, 0.3, 0.3)
        left_toes = HumanoidSkeletonLeftToes(glm.vec3(0, -0.1, 0.08), 0.05)
        right_toes = HumanoidSkeletonRightToes(glm.vec3(0, -0.1, 0.08), 0.05)
        left_hand = HumanoidHand.create_default(BoneFlags.Left)
        right_hand = HumanoidHand.create_default(BoneFlags.Right)
        return HumanoidSkeleton(
            trunk=trunk,
            left_leg=left_leg, right_leg=right_leg,
            left_toes=left_toes, right_toes=right_toes,
            left_arm=left_arm, right_arm=right_arm,
            left_hand=left_hand, right_hand=right_hand)

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

        if self.left_hand:
            self.left_hand.to_node(root[HumanoidBone.leftHand])
        if self.right_hand:
            self.right_hand.to_node(root[HumanoidBone.rightHand])

        return root
