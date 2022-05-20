from typing import NamedTuple, List, Optional, Union
from enum import Enum, auto
import glm
from .humanoid_bones import HumanoidBone
from .coordinate import Coordinate


class HeadTailAxis(Enum):
    XPositive = auto()
    XNegative = auto()
    YPositive = auto()
    YNegative = auto()
    ZPositive = auto()
    ZNegative = auto()
    Other = auto()


class SecondAxis(Enum):
    XPositive = auto()
    XNegative = auto()
    YPositive = auto()
    YNegative = auto()
    ZPositive = auto()
    ZNegative = auto()


class TR(NamedTuple):
    translation: glm.vec3 = glm.vec3(0, 0, 0)
    rotation: glm.quat = glm.quat()

    @staticmethod
    def from_matrix(m: glm.mat4) -> 'TR':
        return TR(m[3].xyz, glm.quat(m))

    def get_matrix(self) -> glm.mat4:
        return glm.translate(self.translation) * glm.mat4(self.rotation)

    def __mul__(self, rhs: 'TR') -> 'TR':
        '''
        R1R2|
        '''
        return TR((self.rotation * glm.vec4(rhs.translation, 1)).xyz + self.translation, self.rotation * rhs.rotation)


class Joint:
    def __init__(self, name: str, local: TR, humanoid_bone: HumanoidBone, *, world: Optional[TR] = None) -> None:
        self.name = name
        self.local = local
        self.world = world if world else TR()
        self.humanoid_bone = humanoid_bone
        self.pose = glm.quat()
        self.children: List[Joint] = []
        self.parent: Optional[Joint] = None

    def add_child(self, child: 'Joint'):
        child.parent = self
        self.children.append(child)
        child.calc_world(self.world)

    def calc_world(self, parent: TR):
        self.world = parent * self.local
        for child in self.children:
            child.calc_world(self.world)


EPSILON = 2e-2


class Bone:
    def __init__(self, head: Joint, tail: Joint) -> None:
        self.head = head
        self.tail = tail

        local_tail_dir = glm.normalize(tail.local.translation)
        if abs(local_tail_dir.x - 1) < EPSILON:
            self.head_tail_axis = HeadTailAxis.XPositive
        elif abs(local_tail_dir.x + 1) < EPSILON:
            self.head_tail_axis = HeadTailAxis.XNegative
        elif abs(local_tail_dir.y - 1) < EPSILON:
            self.head_tail_axis = HeadTailAxis.YPositive
        elif abs(local_tail_dir.y + 1) < EPSILON:
            self.head_tail_axis = HeadTailAxis.YNegative
        elif abs(local_tail_dir.z - 1) < EPSILON:
            self.head_tail_axis = HeadTailAxis.ZPositive
        elif abs(local_tail_dir.z + 1) < EPSILON:
            self.head_tail_axis = HeadTailAxis.ZNegative
        else:
            self.head_tail_axis = HeadTailAxis.Other

        self.second_axis = None
        if self.head_tail_axis != HeadTailAxis.Other:
            world_second = self.head.humanoid_bone.world_second
            m = glm.mat4(self.head.world.get_matrix())
            d0 = glm.dot(m[0].xyz, world_second)
            d1 = glm.dot(m[1].xyz, world_second)
            d2 = glm.dot(m[2].xyz, world_second)
            if abs(d0) > abs(d1) and abs(d0) > abs(d2):
                if d0 > 0:
                    self.second_axis = SecondAxis.XPositive
                else:
                    self.second_axis = SecondAxis.XNegative
            elif abs(d1) > abs(d0) and abs(d1) > abs(d2):
                if d1 > 0:
                    self.second_axis = SecondAxis.YPositive
                else:
                    self.second_axis = SecondAxis.YNegative
            elif abs(d2) > abs(d0) and abs(d2) > abs(d1):
                if d2 > 0:
                    self.second_axis = SecondAxis.ZPositive
                else:
                    self.second_axis = SecondAxis.ZNegative
            else:
                raise RuntimeError()

    def get_length(self) -> float:
        return glm.length(self.tail.world.translation - self.head.world.translation)

    def get_coordinate(self) -> Coordinate:
        match self.head_tail_axis, self.second_axis:
            case HeadTailAxis.XPositive, SecondAxis.YPositive:
                return Coordinate(
                    yaw=glm.vec3(0, 1, 0),
                    pitch=glm.vec3(0, 0, 1),
                    roll=glm.vec3(1, 0, 0),
                )
            case HeadTailAxis.XPositive, SecondAxis.YNegative:
                return Coordinate(
                    yaw=glm.vec3(0, -1, 0),
                    pitch=glm.vec3(0, 0, -1),
                    roll=glm.vec3(1, 0, 0),
                )
            case HeadTailAxis.XPositive, SecondAxis.ZPositive:
                return Coordinate(
                    yaw=glm.vec3(0, 0, 1),
                    pitch=glm.vec3(0, -1, 0),
                    roll=glm.vec3(1, 0, 0),
                )
            case HeadTailAxis.XNegative, SecondAxis.YNegative:
                return Coordinate(
                    yaw=glm.vec3(0, 1, 0),
                    pitch=glm.vec3(0, 0, 1),
                    roll=glm.vec3(1, 0, 0),
                )
            case _:
                raise NotImplementedError()

    def calc_world_matrix(self, parent: glm.mat4) -> glm.mat4:
        m = parent * self.head.local.get_matrix() * glm.mat4(self.head.pose)
        self.head.world = TR.from_matrix(m)
        return m

    def strict_tpose(self):
        pass


class BodyBones(NamedTuple):
    hips: Bone
    spine: Bone
    chest: Bone
    neck: Bone
    head: Bone

    @staticmethod
    def create(hips: Joint, spine: Joint, chest: Joint, neck: Joint, head: Joint, end: Joint) -> 'BodyBones':
        return BodyBones(
            Bone(hips, spine),
            Bone(spine, chest),
            Bone(chest, neck),
            Bone(neck, head),
            Bone(head, end))


class LegBones(NamedTuple):
    upper: Bone
    lower: Bone
    foot: Bone
    toes: Bone

    @staticmethod
    def create(upper: Joint, lower: Joint, foot: Joint, toes: Joint, end: Joint) -> 'LegBones':
        return LegBones(
            Bone(upper, lower),
            Bone(lower, foot),
            Bone(foot, toes),
            Bone(toes, end)
        )


class FingerBones(NamedTuple):
    proximal: Bone
    intermediate: Bone
    distal: Bone

    @staticmethod
    def create(proximal: Joint, intermediate: Joint, distal: Joint, end: Joint):
        return FingerBones(
            Bone(proximal, intermediate),
            Bone(intermediate, distal),
            Bone(distal, end))


class ArmBones(NamedTuple):
    shoulder: Bone
    upper: Bone
    lower: Bone
    hand: Bone
    thumb: Optional[FingerBones] = None
    index: Optional[FingerBones] = None
    middle: Optional[FingerBones] = None
    ring: Optional[FingerBones] = None
    little: Optional[FingerBones] = None

    @staticmethod
    def create(shoulder: Joint, upper: Joint, lower: Joint, hand: Joint, *,
               middle: Union[Joint, FingerBones],
               thumb: Optional[FingerBones] = None,
               index: Optional[FingerBones] = None,
               ring: Optional[FingerBones] = None,
               little: Optional[FingerBones] = None
               ) -> 'ArmBones':
        if isinstance(middle, FingerBones):
            return ArmBones(
                Bone(shoulder, upper),
                Bone(upper, lower),
                Bone(lower, hand),
                Bone(hand, middle.proximal.head),
                thumb=thumb,
                index=index,
                middle=middle,
                ring=ring,
                little=little
            )
        else:
            return ArmBones(
                Bone(shoulder, upper),
                Bone(upper, lower),
                Bone(lower, hand),
                Bone(hand, middle),
                middle=None,
            )


class Skeleton:
    def __init__(self, body: BodyBones,
                 left_leg: Optional[LegBones] = None, right_leg: Optional[LegBones] = None,
                 left_arm: Optional[ArmBones] = None, right_arm: Optional[ArmBones] = None) -> None:
        self.body = body
        self.left_leg = left_leg
        self.right_leg = right_leg
        self.left_arm = left_arm
        self.right_arm = right_arm

    def calc_world_matrix(self):
        m = glm.mat4()
        m = self.body.hips.calc_world_matrix(m)
        m = self.body.spine.calc_world_matrix(m)
        m = self.body.chest.calc_world_matrix(m)
        m = self.body.neck.calc_world_matrix(m)
        m = self.body.head.calc_world_matrix(m)

    def strict_tpose(self):
        self.body.hips.strict_tpose()

    def clear_pose(self):
        pass
