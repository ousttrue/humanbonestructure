from typing import Dict, Optional, Tuple, Iterable
import ctypes
import struct
import pathlib
import json
import logging
import glm
from humanoid.humanoid_bones import HumanoidBone
from . import typed_gltf
from .buffer_types import Float2, Float3, Float4, UShort4, Mat4
LOGGER = logging.getLogger(__name__)


class BytesReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def bytes(self, length: int) -> bytes:
        data = self.data[self.pos:self.pos+length]
        self.pos += length
        return data

    def uint32(self) -> int:
        data = self.bytes(4)
        return struct.unpack('I', data)[0]


class Gltf:
    def __init__(self, gltf: typed_gltf.glTF, *, bin: Optional[bytes] = None, base_dir: Optional[pathlib.Path] = None) -> None:
        self.gltf = gltf
        self.bin = bin
        self.base_dir = base_dir

        self.vrm = None
        if self.get_vrm0_human_bone_map():
            self.vrm = 0
        elif self.get_vrm1_human_bone_map():
            self.vrm = 1

    def get_info(self) -> Iterable[str]:
        match self.vrm:
            case 0:
                yield 'left-handed, T-Stance'
                yield 'world-axis'

            case 1:
                yield 'left-handed, T-Stance'
                yield 'unknown_axis'

            case _:
                yield 'left-handed, unknown'

        yield 'unit: meter'

    def get_vrm0_human_bone_map(self) -> Dict[int, HumanoidBone]:
        if extensions := self.gltf.get('extensions'):
            if vrm0 := extensions.get('VRM'):
                # vrm-0.x
                if humanoid := vrm0.get('humanoid'):
                    if human_bones := humanoid.get('humanBones'):
                        return {b['node']: HumanoidBone(b['bone']) for b in human_bones}
        return {}

    def get_vrm1_human_bone_map(self) -> Dict[int, HumanoidBone]:
        if extensions := self.gltf.get('extensions'):
            if vrm1 := extensions.get('VRMC_vrm'):
                # vrm-1.0
                if humanoid := vrm1.get('humanoid'):
                    if human_bones := humanoid.get('humanBones'):
                        return {v['node']: HumanoidBone[k] for k, v in human_bones.items()}
        return {}

    @staticmethod
    def load_glb(data: bytes) -> 'Gltf':
        '''
        https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.html#glb-file-format-specification
        '''

        r = BytesReader(data)

        assert r.uint32() == 0x46546C67
        assert r.uint32() == 2

        length = r.uint32()

        json_chunk_data = b''
        bin_chunk_data = b''
        while r.pos < length:
            # read chunk
            chunk_length = r.uint32()
            chunk_type = r.uint32()
            chunk_data = r.bytes(chunk_length)

            match chunk_type:
                case 	0x4E4F534A:
                    json_chunk_data = chunk_data
                case 	0x004E4942:
                    bin_chunk_data = chunk_data
                case _:
                    LOGGER.warn(f'')
                    pass

        assert json_chunk_data
        assert bin_chunk_data

        return Gltf(json.loads(json_chunk_data), bin=bin_chunk_data)

    def get_bufferview(self, index: int) -> bytes:
        assert self.bin
        bufferview: typed_gltf.BufferView = self.gltf.get('bufferViews', [])[
            index]
        offset = bufferview.get('byteOffset', 0)
        length = bufferview['byteLength']
        return self.bin[offset:offset+length]

    def load_accessor(self, index: int) -> ctypes.Array:
        accessor: typed_gltf.Accessor = self.gltf.get('accessors', [])[index]
        bufferview_index = accessor.get('bufferView')
        assert isinstance(bufferview_index, int)
        data = self.get_bufferview(bufferview_index)
        byteoffset = accessor.get('byteOffset')
        if byteoffset:
            data = data[byteoffset:]

        match accessor:
            case {'componentType': typed_gltf.AccessorComponentType.UNSIGNED_SHORT.value, 'type': 'SCALAR', 'count': count}:
                buffer_type = ctypes.c_uint16 * count
                return buffer_type.from_buffer_copy(data)
            case {'componentType': typed_gltf.AccessorComponentType.UNSIGNED_INT.value, 'type': 'SCALAR', 'count': count}:
                buffer_type = ctypes.c_uint32 * count
                return buffer_type.from_buffer_copy(data)
            case {'componentType': typed_gltf.AccessorComponentType.FLOAT.value, 'type': 'VEC2', 'count': count}:
                buffer_type = Float2 * count
                return buffer_type.from_buffer_copy(data)
            case {'componentType': typed_gltf.AccessorComponentType.FLOAT.value, 'type': 'VEC3', 'count': count}:
                buffer_type = Float3 * count
                return buffer_type.from_buffer_copy(data)
            case {'componentType': typed_gltf.AccessorComponentType.FLOAT.value, 'type': 'VEC4', 'count': count}:
                buffer_type = Float4 * count
                return buffer_type.from_buffer_copy(data)
            case {'componentType': typed_gltf.AccessorComponentType.FLOAT.value, 'type': 'MAT4', 'count': count}:
                buffer_type = Mat4 * count
                return buffer_type.from_buffer_copy(data)
            case {'componentType': typed_gltf.AccessorComponentType.UNSIGNED_SHORT.value, 'type': 'VEC4', 'count': count}:
                buffer_type = UShort4 * count
                return buffer_type.from_buffer_copy(data)
            case _:
                raise NotImplementedError()


def vertices_indices_len(gltf: typed_gltf.glTF, gltf_mesh: typed_gltf.Mesh) -> Tuple[int, int]:
    vertex_count = 0
    index_count = 0

    accessors = gltf.get('accessors')
    assert accessors
    for gltf_prim in gltf_mesh['primitives']:
        match gltf_prim:
            case {'attributes': {'POSITION': position}, 'indices': indices}:
                position_accessor = accessors[position]
                vertex_count += position_accessor['count']

                indices_accessor = accessors[indices]
                index_count += indices_accessor['count']

            case _:
                NotImplementedError()

    return vertex_count, index_count


def get_trs(gltf_node: typed_gltf.Node) -> Tuple[glm.vec3, glm.quat, glm.vec3]:
    m = gltf_node.get('matrix')
    if m:
        mat = glm.mat4(*m)
        t = glm.vec3()
        r = glm.quat()
        s = glm.vec3()
        sk = glm.vec3()
        tp = glm.vec4()
        if not glm.decompose(mat, s, r, t, sk, tp):
            raise RuntimeError('glm.decompose')
        return t, r, s

    t = gltf_node.get('translation', (0, 0, 0))
    r = gltf_node.get('rotation', (0, 0, 0, 1))
    s = gltf_node.get('scale', (1, 1, 1))
    return glm.vec3(*t), glm.quat(r[3], r[0], r[1], r[2]), glm.vec3(*s)
