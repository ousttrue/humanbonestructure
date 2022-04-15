from typing import List
import glm
from ...formats import pmx_loader, pmd_loader
from ..node import Node
from ..mesh_renderer import MeshRenderer


def build(pmx: pmx_loader.Pmx) -> Node:
    root = Node(-1, '__root__', position=glm.vec3(0, 0, 0))

    # build node hierarchy
    nodes: List[Node] = []
    for i, b in enumerate(pmx.bones):
        node = Node(i, b.name_ja, position=glm.vec3(b.position.x, b.position.y,
                                                    -b.position.z  # reverse z
                                                    ))
        nodes.append(node)

    for i, (node, bone) in enumerate(zip(nodes, pmx.bones)):
        if humanoid_bone := pmd_loader.BONE_HUMANOID_MAP.get(node.name):
            node.humanoid_bone = humanoid_bone

        if bone.parent_index == -1:
            root.add_child(node)
        else:
            parent = nodes[bone.parent_index]
            parent.add_child(node)

    # reverse z
    for i, v in enumerate(pmx.vertices):
        v.position = v.position.reverse_z()
        v.normal = v.normal.reverse_z()

    # set renderer
    root.renderer = MeshRenderer("assets/shader",
                                 pmx.vertices, pmx.indices, joints=nodes, flip=True)

    return root
