import glm
from .node import Node
from ..formats.humanoid_bones import HumanoidBone
from ..formats.transform import Transform


def mod(head: Node, tail: Node):
    # print(head, tail)
    inv = glm.inverse(head.world_matrix)

    # local to
    x = glm.normalize((inv * tail.world_matrix)[3].xyz)
    _z = (inv * glm.vec4(0, 0, 1, 0)).xyz
    y = glm.normalize(glm.cross(_z, x))
    z = glm.normalize(glm.cross(x, y))
    local_from = glm.quat(glm.mat3(x, y, z))

    # local from
    local_to = glm.quat(inv)

    local = local_to * glm.inverse(local_from)
    head.delta = glm.normalize(local)
    print(head, local)


def make_tpose(root: Node):

    upper_arm = root.find(lambda node: node.humanoid_bone ==
                          HumanoidBone.leftUpperArm)
    if not upper_arm:
        return

    for node, _ in upper_arm.traverse_node_and_parent():
        if not node.humanoid_bone:
            continue
        if node.humanoid_bone == HumanoidBone.leftHand:
            continue
        if node.humanoid_tail:
            root.calc_skinning(glm.mat4())
            mod(node, node.humanoid_tail)

    root.calc_skinning(glm.mat4())
