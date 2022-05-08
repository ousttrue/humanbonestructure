from typing import List
import glm
from ...formats import pmd_loader, bytesreader, buffer_types
from ...humanoid.transform import Transform
from ...humanoid.humanoid_bones import HumanoidBone
from ..node import Node
from ..mesh_renderer import MeshRenderer


def reverse_z(v: glm.vec3) -> glm.vec3:
    return glm.vec3(v.x, v.y, -v.z)


def build(pmd: pmd_loader.Pmd) -> Node:
    root = Node('__root__', Transform.identity())

    # build node hierarchy
    nodes: List[Node] = []
    for i, b in enumerate(pmd.bones):
        name = bytesreader.bytes_to_str(b.name)
        node = Node(name, Transform.identity(), pmd_loader.BONE_HUMANOID_MAP.get(
            name, HumanoidBone.unknown))
        node.has_weighted_vertices = i in pmd.deform_bones
        nodes.append(node)

    for i, (node, bone) in enumerate(zip(nodes, pmd.bones)):
        node.humanoid_bone = pmd_loader.BONE_HUMANOID_MAP.get(
            node.name, HumanoidBone.unknown)

        t = glm.vec3(*bone.position)
        if bone.parent_index == 65535:
            node.init_trs = node.init_trs._replace(translation=reverse_z(t))
            root.add_child(node)
        else:
            parent = nodes[bone.parent_index]
            t -= glm.vec3(*pmd.bones[bone.parent_index].position)
            node.init_trs = node.init_trs._replace(translation=reverse_z(t))
            parent.add_child(node)

    # setup vertex and skinning
    vertices = (buffer_types.Vertex4BoneWeights * len(pmd.vertices))()
    # skining_info = (SkinningInfo * len(pmd.vertices))()
    for i, v in enumerate(pmd.vertices):
        vv = v.render
        o = v.option
        dst = vertices[i]
        dst.position = vv.position.reverse_z()
        dst.normal = vv.normal.reverse_z()
        dst.uv = vv.uv
        dst.bone = buffer_types.Float4(o.bone0, o.bone1, 0, 0)
        w = o.weight * 0.01
        dst.weight = buffer_types.Float4(w, 1-w, 0, 0)

        # skining_info[i] = SkinningInfo(
        #     Float3(vv.position.x, vv.position.y, vv.position.z),
        #     UShort4(o.bone0, o.bone1, 0, 0),
        #     Float4(w, 1-w, 0, 0))

    for i in range(0, len(pmd.indices), 3):
        i0, i1, i2 = pmd.indices[i:i+3]
        pmd.indices[i+0] = i0
        pmd.indices[i+1] = i2
        pmd.indices[i+2] = i1

    # set renderer
    root.renderer = MeshRenderer("assets/shader",
                                 vertices, pmd.indices, joints=nodes)
    return root
