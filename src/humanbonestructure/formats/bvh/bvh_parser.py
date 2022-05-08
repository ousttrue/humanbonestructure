from typing import Iterable, Iterator, Optional, List, Set
import logging
import pathlib
import ctypes
import glm
from ...humanoid.humanoid_bones import HumanoidBone
from ...humanoid.pose import Motion, Pose, BonePose
from ...humanoid.transform import Transform
from .bvh_node import Node, Channels

LOGGER = logging.getLogger(__name__)


class BvhException(RuntimeError):
    pass


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
                        node = Node(name, HumanoidBone.unknown, offset,
                                    Channels.PosXYZ_RotZXY, [])
                    case 'CHANNELS', '3', 'Zrotation', 'Xrotation', 'Yrotation':
                        node = Node(name, HumanoidBone.unknown,
                                    offset, Channels.RotZXY, [])
                    # ZYX
                    case 'CHANNELS', '6', 'Xposition', 'Yposition', 'Zposition', 'Zrotation', 'Yrotation', 'Xrotation':
                        node = Node(name, HumanoidBone.unknown, offset,
                                    Channels.PosXYZ_RotZYX, [])
                    case 'CHANNELS', '3', 'Zrotation', 'Yrotation', 'Xrotation':
                        node = Node(name, HumanoidBone.unknown,
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


class Bvh(Motion):
    def __init__(self, path: pathlib.Path, root: Node, frametime: float, frame_count: int, data: ctypes.Array) -> None:
        super().__init__(path.stem)
        self.path = path
        self.root = root
        self.frametime = frametime
        self.fps = 1 / self.frametime
        self.frame_count = frame_count
        self.data = data

        # decide human bone
        from . import humanoid_map
        humanoid_map.resolve(self.root)

        # modify scale
        from .skeleton_checker import SkeletonChecker
        checker = SkeletonChecker(self.root)
        self.forward = checker.forward
        self.unit = checker.get_unit()
        # h = ToMeterScale(self.root)
        self.scale = self.unit.to_meter()

        for node in self.root.traverse():
            node.offset *= self.scale

        # 接地させる
        # self.root.offset.y = h.hips_height * self.scale
        # ヒエラルキーでは原点だが、モーションは接地していた。

        # frame
        self.channel_count = self.root.get_channel_count()
        self.current_frame = -1
        self.set_time(0)

    def set_time(self, time_sec: float):
        frame = int(time_sec * self.fps)
        if frame == self.current_frame:
            return
        if frame < 0:
            frame = 0
        elif frame >= self.frame_count:
            frame = self.frame_count-1
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

    def get_end_time(self):
        return self.frametime * self.frame_count

    def get_frame_count(self) -> int:
        return self.frame_count

    def get_info(self) -> Iterable[str]:
        yield 'right-handed, T-stance'
        yield 'world-axis'
        yield f'unit: {self.unit}, origin: world'
        yield f'{self.frame_count}frames, {self.get_end_time():0.2f}sec'

    def get_humanbones(self) -> Set[HumanoidBone]:
        return set()

    def get_current_pose(self) -> Pose:
        return self.pose


def parse(path: pathlib.Path, src: str) -> Bvh:
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

    return Bvh(path, root, frametime, frames, data)


def from_path(path: pathlib.Path) -> Bvh:
    return parse(path, path.read_text(encoding='utf-8'))
