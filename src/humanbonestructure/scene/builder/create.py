from typing import List
import ctypes
import glm
from ..scene import Scene, Node
from ..mesh_renderer import MeshRenderer
from ...formats.humanoid_bones import HumanoidBone
from ...formats.buffer_types import Float2, Float3, Float4


class Vertex(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('position', Float3),
        ('color', Float3),
        ('bone', Float4),
        ('weight', Float4),
    ]


class Hand:
    def __init__(self) -> None:
        self.vertices = []
        self.indices = []
        self.root = Node(0, '__root__', position=glm.vec3(0))
        self.nodes: List[Node] = [self.root]
        self.current = self.root

        w = 0.04
        self.hand_h = 0.1
        self.push_quad(0, Float3(1, 1, 1),
                       Float3(0, 0, -w),
                       Float3(0+self.hand_h, 0, -w),
                       Float3(0+self.hand_h, 0, +w),
                       Float3(0, 0, +w),
                       )

        self.x_offset = 0.01
        self.y_offset = -0.02
        self.y_size = 0.02
        self.z_offset = w
        self.z_size = 0

    def push_quad(self, bone_index: int, color: Float3, p0: Float3, p1: Float3, p2: Float3, p3: Float3):
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

    def new_finger(self, shift):
        self.current = self.root
        if self.y_offset:
            self.y_size = 0
            self.y_offset = 0
            self.z_offset += shift * 0.5
        else:
            self.z_offset += shift
        self.z_size = shift
        self.x_offset = self.hand_h

    def push_finger(self, humanoidbone: HumanoidBone, l: float, color: Float3):
        '''
        quad
        '''
        x = self.x_offset
        y = self.y_offset
        yw = self.y_size * 0.5 * 0.95
        z = self.z_offset
        zw = self.z_size * 0.5 * 0.95

        node = Node(len(self.nodes), 'leftIndex1', position=glm.vec3(x, y, z))
        node.humanoid_bone = humanoidbone
        self.current.add_child(node)
        self.nodes.append(node)
        self.current = node

        self.push_quad(
            node.index, color,
            Float3(x, y-yw, z-zw),
            Float3(x, y+yw, z+zw),
            Float3(x+l, y+yw, z+zw),
            Float3(x+l, y-yw, z-zw),
        )

        self.x_offset += l

    def create_array(self):
        vertices = (Vertex * len(self.vertices))(*self.vertices)
        indices = (ctypes.c_uint16 * len(self.indices))(*self.indices)
        return vertices, indices


def create_scene(scene: Scene):
    # pos, nom, uv, bone, weight
    #
    # LeftIndex1
    #
    # 3  2
    # +--+
    # |  |
    # +--+
    # 0  1
    hand = Hand()
    # thumb
    red = Float3(1, 0, 0)
    green = Float3(0, 1, 0)
    blue = Float3(0, 0, 1)
    hand.push_finger(HumanoidBone.leftThumbProximal, 0.05, red)
    hand.push_finger(HumanoidBone.leftThumbIntermediate, 0.03, green)
    hand.push_finger(HumanoidBone.leftThumbDistal, 0.02, blue)
    hand.new_finger(-0.02)
    hand.push_finger(HumanoidBone.leftIndexProximal, 0.05, red)
    hand.push_finger(HumanoidBone.leftIndexIntermediate, 0.03, green)
    hand.push_finger(HumanoidBone.leftIndexDistal, 0.02, blue)
    hand.new_finger(-0.02)
    hand.push_finger(HumanoidBone.leftMiddleProximal, 0.05, red)
    hand.push_finger(HumanoidBone.leftMiddleIntermediate, 0.03, green)
    hand.push_finger(HumanoidBone.leftMiddleDistal, 0.02, blue)
    hand.new_finger(-0.02)
    hand.push_finger(HumanoidBone.leftRingProximal, 0.05, red)
    hand.push_finger(HumanoidBone.leftRingIntermediate, 0.03, green)
    hand.push_finger(HumanoidBone.leftRingDistal, 0.02, blue)
    hand.new_finger(-0.02)
    hand.push_finger(HumanoidBone.leftLittleProximal, 0.05, red)
    hand.push_finger(HumanoidBone.leftLittleIntermediate, 0.03, green)
    hand.push_finger(HumanoidBone.leftLittleDistal, 0.02, blue)
    vertices, indices = hand.create_array()

    scene.nodes = hand.nodes[:]
    scene.roots.append(hand.root)
    hand.root.renderer = MeshRenderer("assets/skeleton",
                                      vertices, indices, joints=scene.nodes)
