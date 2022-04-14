from typing import List
import ctypes
from ..formats.buffer_types import Float3, Float4
from .node import Node
from .mesh_renderer import MeshRenderer
from ..formats.humanoid_bones import HumanoidBone


class Vertex(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('position', Float3),
        ('color', Float3),
        ('bone', Float4),
        ('weight', Float4),
    ]


class Skeleton:
    def __init__(self, root: Node) -> None:
        self.nodes: List[Node] = []
        self.vertices = []
        self.indices = []

        bones = [(parent, node)
                 for node, parent in root.traverse_node_and_parent() if parent]

        for head, tail in bones:
            self._add_node(head, tail, Float3(1, 0, 0)
                           if head.humanoid_bone == HumanoidBone.leftIndexIntermediate else Float3(1, 1, 1))

        vertices = (Vertex * len(self.vertices))(*self.vertices)
        indices = (ctypes.c_uint16 * len(self.indices))(*self.indices)

        self.renderer = MeshRenderer("assets/skeleton",
                                     vertices, indices, joints=self.nodes)

    def _add_node(self, head: Node, tail: Node, color: Float3):
        print(head.name, tail.name)
        p0 = head.world_matrix[3]
        p1 = tail.world_matrix[3]
        self._push_triangle(len(self.nodes), color,
                            Float3(p0.x, p0.y, p0.z),
                            Float3(p1.x, p1.y, p1.z),
                            Float3(p0.x, p0.y, p0.z + 0.01),
                            )
        self.nodes.append(head)

    def _push_triangle(self, bone_index: int, color: Float3, p0: Float3, p1: Float3, p2: Float3):
        vertex_index = len(self.vertices)
        self.vertices.append(
            Vertex(p0, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p1, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p2, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))

        self.indices.append(vertex_index)
        self.indices.append(vertex_index+1)
        self.indices.append(vertex_index+2)

    def _push_quad(self, bone_index: int, color: Float3, p0: Float3, p1: Float3, p2: Float3, p3: Float3):
        vertex_index = len(self.vertices)
        self.vertices.append(
            Vertex(p0, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p1, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p2, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))
        self.vertices.append(
            Vertex(p3, color,
                   Float4(bone_index, 0, 0, 0), Float4(1, 0, 0, 0)))

        self.indices.append(vertex_index)
        self.indices.append(vertex_index+1)
        self.indices.append(vertex_index+2)

        self.indices.append(vertex_index+2)
        self.indices.append(vertex_index+3)
        self.indices.append(vertex_index)
