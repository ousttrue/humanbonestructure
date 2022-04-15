from typing import List, NamedTuple, Optional
import ctypes
import glm
from ..formats.buffer_types import Float3, Float4
from .node import Node
from .mesh_renderer import MeshRenderer
from ..formats.humanoid_bones import HumanoidBone


def vec3_to_float3(v: glm.vec3) -> Float3:
    return Float3(v.x, v.y, v.z)


def get_normal(p0: Float3, p1: Float3, p2: Float3) -> Float3:
    pp0 = glm.vec3(*p0)
    pp1 = glm.vec3(*p1)
    pp2 = glm.vec3(*p2)
    n = glm.cross(glm.normalize(pp2-pp1), glm.normalize(pp0-pp1))
    return vec3_to_float3(n)


SHADER = "assets/skeleton"


class Vertex(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('position', Float3),
        ('normal', Float3),
        ('color', Float3),
        ('bone', Float4),
        ('weight', Float4),
    ]


class Bone(NamedTuple):
    head: Node
    tail: Node
    up: glm.vec3
    color: Float3


class Skeleton:
    def __init__(self, root: Node) -> None:
        self.nodes: List[Node] = []
        self.vertices = []
        self.indices = []

        bones: List[Bone] = []

        def find_tail(node: Node) -> Optional[Node]:
            if len(node.children) > 1:
                match node.name:
                    case '上半身2':
                        return next(iter(node for node, _ in node.traverse_node_and_parent() if node.name == '首'))
                    case '下半身':
                        for child in node.children:
                            if find_tail(child):
                                return child
                    case _:
                        pass

            for child in node.children:
                if child.humanoid_bone:
                    return child
                tail = find_tail(child)
                if tail:
                    return tail
            if node.children:
                return node.children[0]

        for node, _ in root.traverse_node_and_parent():
            if node.humanoid_bone:
                tail = find_tail(node)
                if tail:
                    color = Float3(1, 1, 1)
                    if node.humanoid_bone.is_finger():
                        if 'Index' in node.humanoid_bone.name or 'Ring' in node.humanoid_bone.name:
                            if node.humanoid_bone.name.endswith("Intermediate"):
                                color = Float3(0.1, 0.4, 0.8)
                            else:
                                color = Float3(0.2, 0.7, 0.9)
                        else:
                            if node.humanoid_bone.name.endswith("Intermediate"):
                                color = Float3(0.8, 0.4, 0.1)
                            else:
                                color = Float3(0.9, 0.7, 0.2)
                    bones.append(
                        Bone(node, tail, glm.vec3(0, 1, 0), color))

        for bone in bones:
            self._add_node(bone.head, bone.tail, bone.color, bone.up)

        vertices = (Vertex * len(self.vertices))(*self.vertices)
        indices = (ctypes.c_uint16 * len(self.indices))(*self.indices)

        self.renderer = MeshRenderer(SHADER,
                                     vertices, indices, joints=self.nodes)

    def _add_node(self, head: Node, tail: Node, color: Float3, up: glm.vec3):
        print(head.name, tail.name)
        p0 = head.world_matrix[3]
        p1 = tail.world_matrix[3]
        if head.humanoid_bone and head.humanoid_bone.is_finger():
            self._push_cube(len(self.nodes), color, glm.vec3(p0.x, p0.y, p0.z), glm.vec3(p1.x, p1.y, p1.z),
                            up, 0.005, 0.001)
        else:
            self._push_triangle(len(self.nodes), color,
                                Float3(p0.x, p0.y, p0.z),
                                Float3(p1.x, p1.y, p1.z),
                                Float3(p0.x, p0.y, p0.z + 0.01),
                                )
            self._push_triangle(len(self.nodes), color,
                                Float3(p0.x, p0.y, p0.z),
                                Float3(p0.x, p0.y, p0.z + 0.01),
                                Float3(p1.x, p1.y, p1.z),
                                )
        self.nodes.append(head)

    def _push_triangle(self, bone_index: int, color: Float3, p0: Float3, p1: Float3, p2: Float3):
        vertex_index = len(self.vertices)
        n = get_normal(p0, p1, p2)
        self.vertices.append(
            Vertex(p0, n, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p1, n, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p2, n, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))

        self.indices.append(vertex_index)
        self.indices.append(vertex_index+1)
        self.indices.append(vertex_index+2)

    def _push_quad(self, bone_index: int, color: Float3, p0: Float3, p1: Float3, p2: Float3, p3: Float3):
        vertex_index = len(self.vertices)
        n = get_normal(p0, p1, p2)
        self.vertices.append(
            Vertex(p0, n, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p1, n, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p2, n, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p3, n, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))

        self.indices.append(vertex_index)
        self.indices.append(vertex_index+1)
        self.indices.append(vertex_index+2)

        self.indices.append(vertex_index+2)
        self.indices.append(vertex_index+3)
        self.indices.append(vertex_index)

    def _push_cube(self, bone_index: int, color: Float3, p0: glm.vec3, p1: glm.vec3,
                   y: glm.vec3, w: float, h: float):
        x = glm.cross(glm.normalize(p1 - p0), y)
        # 3 2
        # 0 1
        p0_0 = p0-x*w-y*h
        p0_1 = p0+x*w-y*h
        p0_2 = p0+x*w+y*h
        p0_3 = p0-x*w+y*h
        p1_0 = p1-x*w-y*h
        p1_1 = p1+x*w-y*h
        p1_2 = p1+x*w+y*h
        p1_3 = p1-x*w+y*h
        # cap
        self._push_quad(bone_index, color,
                        vec3_to_float3(p1_0),
                        vec3_to_float3(p1_3),
                        vec3_to_float3(p1_2),
                        vec3_to_float3(p1_1))
        # top
        self._push_quad(bone_index, color,
                        vec3_to_float3(p0_3),
                        vec3_to_float3(p0_2),
                        vec3_to_float3(p1_2),
                        vec3_to_float3(p1_3))
        # bottom
        self._push_quad(bone_index, color,
                        vec3_to_float3(p0_1),
                        vec3_to_float3(p0_0),
                        vec3_to_float3(p1_0),
                        vec3_to_float3(p1_1))
        # left
        self._push_quad(bone_index, color,
                        vec3_to_float3(p0_0),
                        vec3_to_float3(p0_3),
                        vec3_to_float3(p1_3),
                        vec3_to_float3(p1_0))
        # right
        self._push_quad(bone_index, color,
                        vec3_to_float3(p0_2),
                        vec3_to_float3(p0_1),
                        vec3_to_float3(p1_1),
                        vec3_to_float3(p1_2))
