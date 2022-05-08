from typing import Set, List, Iterable
import ctypes
import glm
from .bytesreader import BytesReader, bytes_to_str
from ..humanoid.pose import Motion, Pose, Transform, BonePose
from ..humanoid.humanoid_bones import HumanoidBone
from .pmd_loader import BONE_HUMANOID_MAP


class KeyFrame(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('bone_name', ctypes.c_byte * 15),
        ('frame', ctypes.c_uint32),
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float),
        ('rx', ctypes.c_float),
        ('ry', ctypes.c_float),
        ('rz', ctypes.c_float),
        ('rw', ctypes.c_float),
        ('interpolation', ctypes.c_byte * 64),
    ]


class BoneCurve:
    def __init__(self, name: str) -> None:
        self.name = name
        self.humanoid_bone = BONE_HUMANOID_MAP.get(name, HumanoidBone.unknown)
        self.key_frames: List[KeyFrame] = []

    def get_transform(self, frame: int) -> Transform:
        # TODO: set time
        k = self.key_frames[0]
        return Transform(glm.vec3(k.x, k.y, k.z), glm.quat(k.rw, k.rx, k.ry, k.rz), glm.vec3(1))


class Vmd(Motion):
    def __init__(self, name: str, target_model: str, curves: List[BoneCurve]) -> None:
        super().__init__(name)
        self.target_model = target_model
        self.curves = curves
        self._humanbones = set(
            curve.humanoid_bone for curve in self.curves if curve.humanoid_bone.is_enable())
        self.set_time(0)
        self.max_frame = 0
        for curve in self.curves:
            # sort key frames by frame number
            curve.key_frames.sort(key=lambda x: x.frame)

            end_frame = curve.key_frames[-1].frame
            if end_frame > self.max_frame:
                self.max_frame = end_frame

        # fixed 30FPS
        self.seconds = self.max_frame / 30

    def get_end_time(self) -> float:
        return self.seconds

    @staticmethod
    def load(name: str, data: bytes) -> 'Vmd':
        r = BytesReader(data)

        signature = r.str(30, encoding='ascii')
        model = r.str(20, encoding='cp932')
        count = r.uint32()
        keyframes = r.array(KeyFrame*count)

        bone_curves = {}
        for keyframe in keyframes:
            bone_name = bytes_to_str(memoryview(keyframe.bone_name).tobytes())
            curve = bone_curves.get(bone_name)
            if not curve:
                curve = BoneCurve(bone_name)
                bone_curves[bone_name] = curve
            curve.key_frames.append(keyframe)

        return Vmd(name, model, list(bone_curves.values()))

    def get_info(self) -> Iterable[str]:
        yield 'left-handed, A-stance'
        yield 'world-axis, inverted-pelvis'
        yield 'unit: 20/1.63'
        yield 'origin: hips'
        yield f'{self.max_frame}frames, {self.seconds:0.2f}sec'

    def get_humanbones(self) -> Set[HumanoidBone]:
        return self._humanbones

    def get_current_pose(self) -> Pose:
        return self._pose

    def set_time(self, time_sec: float):
        self._pose = Pose(f'{self.name}:{time_sec}sec')
        frame = int(time_sec * 30)  # 30 FPS
        for curve in self.curves:
            t = curve.get_transform(frame)
            self._pose.bones.append(
                BonePose(curve.name, curve.humanoid_bone, t).reverse_z())
