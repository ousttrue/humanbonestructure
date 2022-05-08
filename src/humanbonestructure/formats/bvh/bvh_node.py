from typing import Optional, List, Iterable
import math
from enum import Enum, auto
import glm
from ...humanoid.humanoid_bones import HumanoidBone
from ...humanoid.transform import Transform


def to_radian(degree):
    return degree / 180.0 * math.pi


class Channels(Enum):
    # ZXY
    PosXYZ_RotZXY = auto()
    RotZXY = auto()
    # ZYX
    PosXYZ_RotZYX = auto()
    RotZYX = auto()

    def count(self) -> int:
        match self:
            case (Channels.PosXYZ_RotZXY | Channels.PosXYZ_RotZYX):
                return 6
            case (Channels.RotZXY | Channels.RotZYX):
                return 3
            case _:
                return 0

    def get_matrix(self, it) -> glm.mat4:
        match self:
            # zxy
            case Channels.PosXYZ_RotZXY:
                t = glm.translate(glm.vec3(next(it), next(it), next(it)))
                z = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 0, 1))
                x = glm.angleAxis(to_radian(next(it)), glm.vec3(1, 0, 0))
                y = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 1, 0))
                return t * glm.mat4(z * x * y)
            case Channels.RotZXY:
                z = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 0, 1))
                x = glm.angleAxis(to_radian(next(it)), glm.vec3(1, 0, 0))
                y = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 1, 0))
                return glm.mat4(z * x * y)
            # zyx
            case Channels.PosXYZ_RotZYX:
                t = glm.translate(glm.vec3(next(it), next(it), next(it)))
                z = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 0, 1))
                y = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 1, 0))
                x = glm.angleAxis(to_radian(next(it)), glm.vec3(1, 0, 0))
                return t * glm.mat4(z * y * x)
            case Channels.RotZYX:
                z = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 0, 1))
                y = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 1, 0))
                x = glm.angleAxis(to_radian(next(it)), glm.vec3(1, 0, 0))
                return glm.mat4(z * y * x)
            case _:
                raise NotImplementedError()

    def get_transform(self, it, scale: float) -> Transform:
        match self:
            # zxy
            case Channels.PosXYZ_RotZXY:
                t = glm.vec3(next(it), next(it), next(it)) * scale
                z = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 0, 1))
                x = glm.angleAxis(to_radian(next(it)), glm.vec3(1, 0, 0))
                y = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 1, 0))
                return Transform(t, z * x * y, glm.vec3(1))
            case Channels.RotZXY:
                z = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 0, 1))
                x = glm.angleAxis(to_radian(next(it)), glm.vec3(1, 0, 0))
                y = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 1, 0))
                return Transform.from_rotation(z * x * y)
            # zyx
            case Channels.PosXYZ_RotZYX:
                t = glm.vec3(next(it), next(it), next(it)) * scale
                z = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 0, 1))
                y = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 1, 0))
                x = glm.angleAxis(to_radian(next(it)), glm.vec3(1, 0, 0))
                return Transform(t, z * y * x, glm.vec3(1))
            case Channels.RotZYX:
                z = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 0, 1))
                y = glm.angleAxis(to_radian(next(it)), glm.vec3(0, 1, 0))
                x = glm.angleAxis(to_radian(next(it)), glm.vec3(1, 0, 0))
                return Transform.from_rotation(z * y * x)
            case _:
                raise NotImplementedError()


class Node:

    def __init__(self,
                 name: Optional[str],
                 humanoid_bone: HumanoidBone,
                 offset: glm.vec3,
                 channels: Optional[Channels],
                 children: List['Node']):
        assert humanoid_bone
        self.name = name
        self.humanoid_bone = humanoid_bone
        self.offset = offset
        self.channels = channels
        self.children = children

    def __str__(self) -> str:
        if self.name:
            return f'{self.name}:{self.offset}:{self.channels}'
        else:
            return f'End Site: {self.offset}'

    def traverse(self) -> Iterable['Node']:
        yield self
        for child in self.children:
            for x in child.traverse():
                yield x

    def get_channel_count(self) -> int:
        count = 0
        for node in self.traverse():
            if node.channels:
                count += node.channels.count()
        return count
