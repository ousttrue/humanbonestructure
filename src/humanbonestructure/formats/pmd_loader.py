'''
https://blog.goo.ne.jp/torisu_tetosuki/e/209ad341d3ece2b1b4df24abf619d6e4
'''
from typing import List, Dict
import ctypes
from .bytesreader import BytesReader
from .humanoid_bones import HumanoidBone
from .buffer_types import Float3, Float4, RenderVertex

SCALING_FACTOR = 1.63/20


BONE_HUMANOID_MAP = {
    '下半身': HumanoidBone.hips,
    '上半身': HumanoidBone.spine,
    '上半身2': HumanoidBone.chest,
    '首': HumanoidBone.neck,
    '頭': HumanoidBone.head,
    '左目': HumanoidBone.leftEye,
    '右目': HumanoidBone.rightEye,

    '左肩': HumanoidBone.leftShoulder,
    '左腕': HumanoidBone.leftUpperArm,
    '左ひじ': HumanoidBone.leftLowerArm,
    '左手首': HumanoidBone.leftHand,
    '右肩': HumanoidBone.rightShoulder,
    '右腕': HumanoidBone.rightUpperArm,
    '右ひじ': HumanoidBone.rightLowerArm,
    '右手首': HumanoidBone.rightHand,

    '左足': HumanoidBone.leftUpperLeg,
    '左ひざ': HumanoidBone.leftLowerLeg,
    '左足首': HumanoidBone.leftFoot,
    '左つま先': HumanoidBone.leftToes,
    '右足': HumanoidBone.rightUpperLeg,
    '右ひざ': HumanoidBone.rightLowerLeg,
    '右足首': HumanoidBone.rightFoot,
    '右つま先': HumanoidBone.rightToes,

    '左親指０': HumanoidBone.leftThumbProximal,
    '左親指１': HumanoidBone.leftThumbIntermediate,
    '左親指２': HumanoidBone.leftThumbDistal,
    '左人指１': HumanoidBone.leftIndexProximal,
    '左人指２': HumanoidBone.leftIndexIntermediate,
    '左人指３': HumanoidBone.leftIndexDistal,
    '左中指１': HumanoidBone.leftMiddleProximal,
    '左中指２': HumanoidBone.leftMiddleIntermediate,
    '左中指３': HumanoidBone.leftMiddleDistal,
    '左薬指１': HumanoidBone.leftRingProximal,
    '左薬指２': HumanoidBone.leftRingIntermediate,
    '左薬指３': HumanoidBone.leftRingDistal,
    '左小指１': HumanoidBone.leftLittleProximal,
    '左小指２': HumanoidBone.leftLittleIntermediate,
    '左小指３': HumanoidBone.leftLittleDistal,

    '右親指０': HumanoidBone.rightThumbProximal,
    '右親指１': HumanoidBone.rightThumbIntermediate,
    '右親指２': HumanoidBone.rightThumbDistal,
    '右人指１': HumanoidBone.rightIndexProximal,
    '右人指２': HumanoidBone.rightIndexIntermediate,
    '右人指３': HumanoidBone.rightIndexDistal,
    '右中指１': HumanoidBone.rightMiddleProximal,
    '右中指２': HumanoidBone.rightMiddleIntermediate,
    '右中指３': HumanoidBone.rightMiddleDistal,
    '右薬指１': HumanoidBone.rightRingProximal,
    '右薬指２': HumanoidBone.rightRingIntermediate,
    '右薬指３': HumanoidBone.rightRingDistal,
    '右小指１': HumanoidBone.rightLittleProximal,
    '右小指２': HumanoidBone.rightLittleIntermediate,
    '右小指３': HumanoidBone.rightLittleDistal,
}


class OptionVertex(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('bone0', ctypes.c_ushort),
        ('bone1', ctypes.c_ushort),
        ('weight', ctypes.c_byte),
        ('flag', ctypes.c_byte),
    ]


class Vertex(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('render', RenderVertex),
        ('option', OptionVertex),
    ]

    def __str__(self) -> str:
        return f'[{self.x}, {self.y}, {self.z}]'


class Submesh(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('rgba', Float4),
        ('specularity', ctypes.c_float),
        ('specular', Float3),
        ('ambient', Float3),
        ('toon_index', ctypes.c_byte),
        ('flag', ctypes.c_byte),
        ('face_vertex_count', ctypes.c_uint32),
        ('texture_name', ctypes.c_byte * 20),
    ]


class Bone(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('name', ctypes.c_byte * 20),
        ('parent_index', ctypes.c_uint16),
        ('tail_index', ctypes.c_uint16),
        ('type', ctypes.c_byte),
        ('ik_index', ctypes.c_uint16),
        ('position', Float3),
    ]


class MorphVertex(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint32),
        ('position', Float3),
    ]


assert ctypes.sizeof(Vertex) == 38
assert ctypes.sizeof(Submesh) == 70
assert ctypes.sizeof(Bone) == 39
assert ctypes.sizeof(MorphVertex) == 16


class Ik:
    def __init__(self, bone_index: int,
                 effector_index: int,
                 iteration_count: int,
                 rotation_limit: float,
                 chain: ctypes.Array):
        self.bone_index = bone_index
        self.effector_index = effector_index
        self.iteration_count = iteration_count
        self.rotation_limit = rotation_limit
        self.chain: List[int] = [c for c in chain]


class Morph:
    def __init__(self, name: str, morph_type: int, vertices: ctypes.Array) -> None:
        self.name = name
        self.morph_type = morph_type
        self.vertices = vertices

    def __str__(self) -> str:
        return f'[{self.morph_type}:{self.name}]'


class Pmd:
    def __init__(self, data):
        assert isinstance(data, bytes)
        r = BytesReader(data)
        assert r.bytes(3) == b'Pmd'
        assert r.float32() == 1.00
        self.name = r.str(20, encoding='cp932')
        self.comment = r.str(256, encoding='cp932')

        vertex_count = r.uint32()
        self.deform_bones: Dict[int, int] = {}
        self.vertices = r.array(Vertex * vertex_count)
        for v in self.vertices:
            v.render.position.x *= SCALING_FACTOR
            v.render.position.y *= SCALING_FACTOR
            v.render.position.z *= SCALING_FACTOR
            self.deform_bones[v.option.bone0] = self.deform_bones.get(
                v.option.bone0, 0)+1
            self.deform_bones[v.option.bone1] = self.deform_bones.get(
                v.option.bone1, 0)+1

        face_vertex_count = r.uint32()
        self.indices = r.array(ctypes.c_uint16 * face_vertex_count)

        submesh_count = r.uint32()
        self.submeshes = r.array(Submesh * submesh_count)

        bone_count = r.uint16()
        self.bones = r.array(Bone * bone_count)
        for b in self.bones:
            b.position.x *= SCALING_FACTOR
            b.position.y *= SCALING_FACTOR
            b.position.z *= SCALING_FACTOR

        self.ik = []
        ik_count = r.uint16()
        for i in range(ik_count):
            bone_index = r.uint16()
            effector_index = r.uint16()
            chain_length = r.uint8()
            iterations = r.uint16()
            rotation_limit = r.float32()
            chain = r.array(ctypes.c_uint16 * chain_length)
            self.ik.append(Ik(bone_index, effector_index,
                           iterations, rotation_limit, chain))

        self.morphs = []
        morph_count = r.uint16()
        for i in range(morph_count):
            name = r.str(20, encoding='cp932')
            vertex_count = r.uint32()
            morph_type = r.uint8()
            morph_vertices = r.array(MorphVertex * vertex_count)
            self.morphs.append(Morph(name, morph_type, morph_vertices))

    def __str__(self) -> str:
        return f'<pmd {self.name}: {len(self.vertices)}vert, {len(self.indices)//3}tri, {len(self.submeshes)}materials, {len(self.bones)}bones, {len(self.ik)}IK, {len(self.morphs)}morphs>'
