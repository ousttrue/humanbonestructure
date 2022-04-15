import glm
from .node import Node
from ..formats.humanoid_bones import HumanoidBone
import copy

def mod(head: Node, tail: Node):
    print(head, tail)

    x = glm.normalize(
        tail.world_matrix[3].xyz-head.world_matrix[3].xyz)
    z = glm.vec3(0, 0, 1)
    y = glm.cross(z, x)
    world = glm.mat4(
        glm.vec4(x, 0),
        glm.vec4(y, 0),
        glm.vec4(z, 0),
        glm.vec4(0, 0, 0, 1))

    src = copy.copy(head.world_matrix)
    src[3] = glm.vec4(0, 0, 0, 1)

    local = glm.inverse(src) * world

    head.delta = glm.quat(local)
    assert head.parent
    head.calc_skinning(head.parent.world_matrix)


def make_tpose(root: Node):

    upper_arm = root.find(lambda node: node.humanoid_bone ==
                          HumanoidBone.leftUpperArm)
    if not upper_arm:
        return

    for node, _ in upper_arm.traverse_node_and_parent():
        if node.humanoid_bone:
            tail = node.find_tail()
            if tail:
                mod(node, tail)
