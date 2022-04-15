from typing import List
import glm
from ...formats import pmx_loader, pmd_loader
from ...formats.transform import Transform
from ..node import Node
from ..mesh_renderer import MeshRenderer
from .pmd_builder import reverse_z


def build(pmx: pmx_loader.Pmx) -> Node:
    root = Node(-1, '__root__',  Transform.identity())

    # build node hierarchy
    nodes: List[Node] = []
    for i, b in enumerate(pmx.bones):
        node = Node(i, b.name_ja, Transform.identity())
        nodes.append(node)

    for i, (node, bone) in enumerate(zip(nodes, pmx.bones)):
        if humanoid_bone := pmd_loader.BONE_HUMANOID_MAP.get(node.name):
            node.humanoid_bone = humanoid_bone

        t = glm.vec3(*bone.position)
        if bone.parent_index == -1:
            node.init_trs = node.init_trs._replace(translation=reverse_z(t))
            root.add_child(node)
        else:
            t -= glm.vec3(*pmx.bones[bone.parent_index].position)
            node.init_trs = node.init_trs._replace(translation=reverse_z(t))
            parent = nodes[bone.parent_index]
            parent.add_child(node)

    # reverse z
    for i, v in enumerate(pmx.vertices):
        v.position = v.position.reverse_z()
        v.normal = v.normal.reverse_z()

    for i in range(0, len(pmx.indices), 3):
        i0, i1, i2 = pmx.indices[i:i+3]
        pmx.indices[i+0] = i0
        pmx.indices[i+1] = i2
        pmx.indices[i+2] = i1

    # set renderer
    root.renderer = MeshRenderer("assets/shader",
                                 pmx.vertices, pmx.indices, joints=nodes)

    return root
