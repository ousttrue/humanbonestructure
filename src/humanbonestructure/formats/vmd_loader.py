from typing import Set, List, Dict
import ctypes
import glm
from .bytesreader import BytesReader, bytes_to_str
from .pose import Motion, Pose, Transform
from .humanoid_bones import HumanoidBone
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
        self.humanoid_bone = BONE_HUMANOID_MAP.get(name)
        self.key_frames: List[Transform] = []


class Vmd(Motion):
    def __init__(self, model: str, curves: Dict[str, BoneCurve]) -> None:
        self.model = model
        self.curves = curves
        self._humanbones = list(
            set(curve.humanoid_bone for curve in self.curves.values() if curve.humanoid_bone))

    @staticmethod
    def load(data: bytes) -> 'Vmd':
        r = BytesReader(data)

        signature = r.str(30, encoding='ascii')
        model = r.str(20, encoding='cp932')
        count = r.uint32()
        key_frames = r.array(KeyFrame*count)

        bone_curves = {}
        for key_frame in key_frames:
            bone_name = bytes_to_str(memoryview(key_frame.bone_name).tobytes())
            curve = bone_curves.get(bone_name)
            if not curve:
                curve = BoneCurve(bone_name)
                bone_curves[bone_name] = curve
            curve.key_frames.append(Transform(
                glm.vec3(key_frame.x, key_frame.y, key_frame.z),
                glm.quat(key_frame.rw, key_frame.rx,
                         key_frame.ry, key_frame.rz),
                glm.vec3(1)))

        return Vmd(model, bone_curves)

    def get_humanbones(self) -> Set[HumanoidBone]:
        raise NotImplementedError()

    def get_current_pose(self) -> Pose:
        raise NotImplementedError()
