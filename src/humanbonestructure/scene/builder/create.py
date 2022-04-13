import ctypes
import glm
from ..scene import Scene, Node
from ..mesh_renderer import MeshRenderer
from ...formats.humanoid_bones import HumanoidBone
from ...formats.buffer_types import Vertex4BoneWeights, Float2, Float3, Float4


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
    w = 0.1
    h = 0.5
    vertices = (Vertex4BoneWeights * 4)(
        Vertex4BoneWeights(Float3(0, 0, -w), Float3(0, 1, 0),
                           Float2(0, 0), Float4(0, 0, 0, 0), Float4(1, 0, 0, 0)),
        Vertex4BoneWeights(Float3(0, 0, w), Float3(0, 1, 0), Float2(
            0, 0), Float4(0, 0, 0, 0), Float4(1, 0, 0, 0)),
        Vertex4BoneWeights(Float3(h, 0, w), Float3(0, 1, 0), Float2(
            0, 0), Float4(0, 0, 0, 0), Float4(1, 0, 0, 0)),
        Vertex4BoneWeights(Float3(h, 0, -w), Float3(0, 1, 0),
                           Float2(0, 0), Float4(0, 0, 0, 0), Float4(1, 0, 0, 0)),
    )
    indices = (ctypes.c_uint16 * 6)(0, 1, 2, 2, 3, 0)

    # build node hierarchy
    node = Node(0, 'leftIndex1', position=glm.vec3(0))
    node.humanoid_bone = HumanoidBone.leftIndexProximal
    scene.nodes.append(node)
    scene.roots.append(node)
    node.renderer = MeshRenderer(
        vertices, indices, joints=scene.nodes)
