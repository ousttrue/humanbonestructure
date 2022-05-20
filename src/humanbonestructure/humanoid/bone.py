from typing import NamedTuple, List, Optional
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


class Joint:
    def __init__(self, name: str, local: TR, humanoid_bone: HumanoidBone, *, world: Optional[TR] = None) -> None:
        self.name = name
        self.local = local
        self.world = world if world else TR()
        self.humanoid_bone = humanoid_bone


EPSILON = 1e-2


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
            case _:
                raise NotImplementedError()


class BodyBones(NamedTuple):
    hips: Bone
    spine: Bone
    chest: Bone
    neck: Bone
    head: Bone

    @staticmethod
    def create(hips: Joint, spine: Joint, chest: Joint, neck: Joint, head: Joint, head_end: Joint) -> 'BodyBones':
        return BodyBones(
            Bone(hips, spine),
            Bone(spine, chest),
            Bone(chest, neck),
            Bone(neck, head),
            Bone(head, head_end))


class Skeleton:
    def __init__(self, body: BodyBones) -> None:
        self.body = body
