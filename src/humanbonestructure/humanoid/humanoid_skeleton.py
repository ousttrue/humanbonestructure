from typing import NamedTuple, Dict
import glm
from ..scene.node import Node
from .humanoid_bones import HumanoidBone


class HumanoidSkeletonTrunk(NamedTuple):
    position: glm.vec3
    hips: float
    spine: float
    chest: float
    neck: float
    head: float


class HumanoidSkeletonArm(NamedTuple):
    position: glm.vec3
    shoulder: float
    upper_arm: float
    lower_arm: float
    hand: float


class HumanoidSkeletonLeg(NamedTuple):
    position: glm.vec3
    upper_leg: float
    lower_leg: float
    foot: float


class HumanoidSkeletonToes(NamedTuple):
    position: glm.vec3
    toes: float


class HumanoidSkeletonFinger(NamedTuple):
    position: glm.vec3
    finger1: float
    finger2: float
    finger3: float


class HumanoidSkeletonFingers(NamedTuple):
    thumbnail: HumanoidSkeletonFinger
    index: HumanoidSkeletonFinger
    middle: HumanoidSkeletonFinger
    ring: HumanoidSkeletonFinger
    little: HumanoidSkeletonFinger


class HumanoidSkeleton:

    def __init__(self,
                 *,
                 trunk: HumanoidSkeletonTrunk,
                 left_leg: HumanoidSkeletonLeg,
                 right_leg: HumanoidSkeletonLeg,
                 left_arm: HumanoidSkeletonArm,
                 right_arm: HumanoidSkeletonArm,
                 #
                 left_toes: HumanoidSkeletonToes,
                 right_toes: HumanoidSkeletonToes,
                 #
                 left_fingers: HumanoidSkeletonFingers,
                 right_fingers: HumanoidSkeletonFingers
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

    @staticmethod
    def from_node(root: Node) -> 'HumanoidSkeleton':
        raise NotImplementedError()

    def to_node(self) -> Node:
        raise NotImplementedError()
