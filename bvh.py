from typing import NamedTuple, Iterator, Optional, List
from enum import Enum, auto


class Channels(Enum):
    PosXYZ_RotZXY = auto()
    RotZXY = auto()


class BvhExceptin(RuntimeError):
    pass

class Float3(NamedTuple):
    x: float
    y: float
    z: float

    def __str__(self)->str:
        return f'[{self.x}, {self.y}, {self.z}]'


class Node(NamedTuple):
    name: Optional[str] # End site has no name
    offset: Float3
    channels: Optional[Channels]
    children: List['Node']

    def __str__(self)->str:
        if self.name:
            return f'{self.name}:{self.offset}:{self.channels}'
        else:
            return f'End Site: {self.offset}'


def parse_offset_channels(it: Iterator[str], name: Optional[str])->Node:
    if next(it).strip() != '{':
        raise BvhExceptin()
    offset = next(it).strip()
    node = None
    match offset.split():
        case 'OFFSET', x, y, z:
            offset = Float3(float(x), float(y), float(z))
            if name:
                channels = next(it).strip()
                node = None
                match channels.split():
                    case 'CHANNELS', '6', 'Xposition', 'Yposition', 'Zposition', 'Zrotation', 'Xrotation', 'Yrotation':
                        node = Node(name, offset, Channels.PosXYZ_RotZXY, [])
                    case 'CHANNELS', '3', 'Zrotation', 'Xrotation', 'Yrotation':
                        node = Node(name, offset, Channels.RotZXY, [])
                    case _:
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
                node= Node(name, offset, None, [])
                close = next(it).strip()
                if close != '}':
                    raise BvhExceptin()
        case _:
            raise BvhExceptin('OFFSET not found')
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


def parse(src: str) -> Node:
    it = iter(src.splitlines())
    if next(it) != 'HIERARCHY':
        raise BvhExceptin('HIERARCHY not found')

    head = next(it).strip()
    root = parse_recursive(it, head)
    if not root:
        raise BvhExceptin('no ROOT')

    if next(it) != 'MOTION':
        raise BvhExceptin('MOTION not found')

    return root
