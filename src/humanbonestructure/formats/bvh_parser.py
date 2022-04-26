from typing import Iterable, NamedTuple, Iterator, Optional, List
from enum import Enum, auto
import ctypes
import math
import glm


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


class BvhException(RuntimeError):
    pass


class Node(NamedTuple):
    name: Optional[str]  # End site has no name
    offset: glm.vec3
    channels: Optional[Channels]
    children: List['Node']

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
                node = None
                match channels.split():
                    # ZXY
                    case 'CHANNELS', '6', 'Xposition', 'Yposition', 'Zposition', 'Zrotation', 'Xrotation', 'Yrotation':
                        node = Node(name, offset, Channels.PosXYZ_RotZXY, [])
                    case 'CHANNELS', '3', 'Zrotation', 'Xrotation', 'Yrotation':
                        node = Node(name, offset, Channels.RotZXY, [])
                    # ZYX
                    case 'CHANNELS', '6', 'Xposition', 'Yposition', 'Zposition', 'Zrotation', 'Yrotation', 'Xrotation':
                        node = Node(name, offset, Channels.PosXYZ_RotZYX, [])
                    case 'CHANNELS', '3', 'Zrotation', 'Yrotation', 'Xrotation':
                        node = Node(name, offset, Channels.RotZYX, [])
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
                node = Node(name, offset, None, [])
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


class Bvh:
    def __init__(self, root: Node, frametime: float, frames: int, data: ctypes.Array) -> None:
        self.root = root
        self.frametime = frametime
        self.frames = frames
        self.data = data

    def get_seconds(self):
        return self.frametime * self.frames


def parse(src: str) -> Bvh:
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

    return Bvh(root, frametime, frames, data)
