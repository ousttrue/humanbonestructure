from typing import Dict
import copy
import glm
from ..scene.node import Node
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
    head.pose = Transform(glm.vec3(0), glm.normalize(local), glm.vec3(1))
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


def pose_to_init(root: Node) -> Dict[Node, glm.quat]:
    delta_map = {}
    for node, parent in root.traverse_node_and_parent():
        r = glm.quat()
        if node.pose:
            r = node.pose.rotation
        if parent:
            node.init_trs = Transform(
                (glm.inverse(parent.world_matrix)
                    * node.world_matrix)[3].xyz,
                node.init_trs.rotation * r,
                glm.vec3(1))
        else:
            node.init_trs = Transform(
                node.world_matrix[3].xyz,
                node.init_trs.rotation * r,
                glm.vec3(1))
        delta_map[node] = glm.inverse(r)
        node.pose = None
    return delta_map


def local_axis_fit_world(root: Node):

    for node, parent in root.traverse_node_and_parent():
        node.local_aixs = glm.inverse(glm.quat(node.world_matrix))

    root.calc_skinning(glm.mat4())
