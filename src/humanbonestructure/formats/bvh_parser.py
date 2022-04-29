from typing import Iterable, NamedTuple, Iterator, Optional, List, Set
import pathlib
from enum import Enum, auto
import ctypes
import math
import glm
from .humanoid_bones import HumanoidBone
from .pose import Motion, Pose, BonePose
from .transform import Transform

HUMANOID_MAP = {
    'Hips': HumanoidBone.hips,
    'Spine': HumanoidBone.spine,
    'Spine1': HumanoidBone.chest,
    'Neck': HumanoidBone.neck,
    'Head': HumanoidBone.head,

    'LeftShoulder': HumanoidBone.leftShoulder,
    'LeftArm': HumanoidBone.leftUpperArm,
    'LeftForeArm': HumanoidBone.leftLowerArm,
    'LeftHand': HumanoidBone.leftHand,

    'RightShoulder': HumanoidBone.rightShoulder,
    'RightArm': HumanoidBone.rightUpperArm,
    'RightForeArm': HumanoidBone.rightLowerArm,
    'RightHand': HumanoidBone.rightHand,

    'LeftUpLeg': HumanoidBone.leftUpperLeg,
    'LeftLeg': HumanoidBone.leftLowerLeg,
    'LeftFoot': HumanoidBone.leftFoot,
    'LeftToeBase': HumanoidBone.leftToes,

    'RightUpLeg': HumanoidBone.rightUpperLeg,
    'RightLeg': HumanoidBone.rightLowerLeg,
    'RightFoot': HumanoidBone.rightFoot,
    'RightToeBase': HumanoidBone.rightToes,
}


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


class BvhException(RuntimeError):
    pass


class Node:

    def __init__(self,
                 name: Optional[str],
                 humanoid_bone: HumanoidBone,
                 offset: glm.vec3,
                 channels: Optional[Channels],
                 children: List['Node']):
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


def parse_offset_channels(it: Iterator[str], name: Optional[str]) -> Node:
    if next(it).strip() != '{':
        raise BvhException()
    offset = next(it).strip()
    node = None
    match offset.split():
        case 'OFFSET', x, y, z:
            offset = glm.vec3(float(x), float(y), float(z))
            if name:
                channels = next(it).strip()
                humanoid_bone = HUMANOID_MAP.get(name, HumanoidBone.unknown)
                node = None
                match channels.split():
                    # ZXY
                    case 'CHANNELS', '6', 'Xposition', 'Yposition', 'Zposition', 'Zrotation', 'Xrotation', 'Yrotation':
                        node = Node(name, humanoid_bone, offset,
                                    Channels.PosXYZ_RotZXY, [])
                    case 'CHANNELS', '3', 'Zrotation', 'Xrotation', 'Yrotation':
                        node = Node(name, humanoid_bone,
                                    offset, Channels.RotZXY, [])
                    # ZYX
                    case 'CHANNELS', '6', 'Xposition', 'Yposition', 'Zposition', 'Zrotation', 'Yrotation', 'Xrotation':
                        node = Node(name, humanoid_bone, offset,
                                    Channels.PosXYZ_RotZYX, [])
                    case 'CHANNELS', '3', 'Zrotation', 'Yrotation', 'Xrotation':
                        node = Node(name, humanoid_bone,
                                    offset, Channels.RotZYX, [])
                    #
                    case _:
                        # CHANNELS 6 Xposition Yposition Zposition Yrotation Xrotation Zrotation
                        # CHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation
                        raise NotImplementedError(channels)
                # children
                while True:
                    head = next(it).strip()
                    if head == '}':
                        break
                    child = parse_recursive(it, head)
                    node.children.append(child)
            else:
                # End Site
                node = Node(name, HumanoidBone.endSite, offset, None, [])
                close = next(it).strip()
                if close != '}':
                    raise BvhException()
        case _:
            raise BvhException('OFFSET not found')
    return node


def parse_recursive(it: Iterator[str], head: str) -> Node:
    match head.split():
        case 'ROOT', name:
            return parse_offset_channels(it, name)
        case 'JOINT', name:
            return parse_offset_channels(it, name)
        case 'End', 'Site':
            return parse_offset_channels(it, None)
        case _:
            raise NotImplementedError()


class ToMeterScale:
    def __init__(self, root: Node):
        self.hips_y = 0
        self.min_y = 0
        self.traverse(root)

        self.hips_height = self.hips_y - self.min_y
        self.scale = 1
        if self.hips_height > 70 and self.hips_height < 100:
            # cm to meter
            self.scale = 0.01

    def traverse(self, node: Node, parent_y=0):
        y = parent_y + node.offset.y
        if node.humanoid_bone == HumanoidBone.hips:
            self.hips_y = y
        if y < self.min_y:
            self.min_y = y
        for child in node.children:
            self.traverse(child, y)


class Bvh(Motion):
    def __init__(self, name: str, root: Node, frametime: float, frame_count: int, data: ctypes.Array) -> None:
        super().__init__(name)
        self.root = root
        self.frametime = frametime
        self.frame_count = frame_count
        self.data = data

        self._meter_scale()

        # frame
        self.channel_count = self.root.get_channel_count()
        self.current_frame = -1
        self.set_frame(0)

    def _meter_scale(self):
        # modify scale
        h = ToMeterScale(self.root)
        self.scale = h.scale

        for node in self.root.traverse():
            node.offset *= self.scale

        # 接地させる
        # self.root.offset.y = h.hips_height * self.scale
        # ヒエラルキーでは原点だが、モーションは接地していた。

    def set_frame(self, frame: int):
        if frame == self.current_frame:
            return
        self.current_frame = frame
        begin = self.channel_count * frame
        data = self.data[begin:begin+self.channel_count]

        self.pose = Pose(f'{frame}')
        it = iter(data)

        def traverse(node: Node):
            if not node.name:
                # endsite
                return
            if node.channels:
                t = node.channels.get_transform(it, self.scale)
            else:
                t = Transform.identity()
            self.pose.bones.append(BonePose(node.name, node.humanoid_bone, t))

            for child in node.children:
                traverse(child)
        traverse(self.root)

    def get_seconds(self):
        return self.frametime * self.frame_count

    def get_frame_count(self) -> int:
        return self.frame_count

    def get_info(self) -> str:
        return f'{self.frame_count}frames, {self.get_seconds()}sec'

    def get_humanbones(self) -> Set[HumanoidBone]:
        return set()

    def get_current_pose(self) -> Pose:
        return self.pose


def parse(name: str, src: str) -> Bvh:
    it = iter(src.splitlines())
    if next(it) != 'HIERARCHY':
        raise BvhException('HIERARCHY not found')

    head = next(it).strip()
    root = parse_recursive(it, head)
    if not root:
        raise BvhException('no ROOT')

    if next(it) != 'MOTION':
        raise BvhException('MOTION not found')

    frames = next(it).strip()
    if not frames.startswith('Frames:'):
        raise BvhException('Frames: not found')
    frames = int(frames[7:])

    frametime = next(it).strip()
    if not frametime.startswith('Frame Time:'):
        raise BvhException('Frame Time: not found')
    frametime = float(frametime[11:])

    channel_count = root.get_channel_count()
    data = (ctypes.c_float * (frames * channel_count))()
    i = 0
    for _ in range(frames):
        for x in next(it).strip().split():
            data[i] = float(x)
            i += 1

    return Bvh(name, root, frametime, frames, data)


def from_path(path: pathlib.Path) -> Bvh:
    return parse(path.stem, path.read_text(encoding='utf-8'))
