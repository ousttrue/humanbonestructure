import glm
from .node import Node
from ..formats.humanoid_bones import HumanoidBone


def mod(head: Node, tail: Node):
    # print(head, tail)

    x = glm.normalize(
        tail.world_matrix[3].xyz-head.world_matrix[3].xyz)
    _z = glm.vec3(0, 0, 1)
    y = glm.cross(_z, x)
    z = glm.cross(x, y)
    world = glm.quat(glm.mat3(x, y, z))

    src = glm.quat()
    local = glm.inverse(world) * src
    head.delta = local
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
        tail = node.find_tail()
        if tail:
            root.calc_skinning(glm.mat4())
            mod(node, tail)

    root.calc_skinning(glm.mat4())
