from typing import Dict, Set
import math
import glm
from ..scene.node import Node
from .humanoid_bones import HumanoidBone
from .transform import Transform
from .pose import Motion, Pose, BonePose


# def mod(head: Node, tail: Node):
#     # print(head, tail)
#     inv = glm.inverse(head.world_matrix)

#     # local to
#     x = glm.normalize((inv * tail.world_matrix)[3].xyz)
#     _z = (inv * glm.vec4(0, 0, 1, 0)).xyz
#     y = glm.normalize(glm.cross(_z, x))
#     z = glm.normalize(glm.cross(x, y))
#     local_from = glm.quat(glm.mat3(x, y, z))

#     # local from
#     local_to = glm.quat(inv)

#     local = local_to * glm.inverse(local_from)
#     head.pose = Transform(glm.vec3(0), glm.normalize(local), glm.vec3(1))
#     print(head, local)


def mod(head: Node, tail: Node, forward: glm.vec3):
    assert not head.pose
    p_tail = tail.local_matrix[3].xyz
    dir = glm.normalize(p_tail)
    target = glm.inverse(glm.quat(head.world_matrix)) * forward
    axis = glm.normalize(glm.cross(dir, target))
    dot = glm.dot(dir, target)
    r = glm.angleAxis(math.acos(dot), axis)
    head.pose = Transform.from_rotation(r)


# def mod(head: Node, tail: Node, forward: glm.vec3):
#     p_head = head.world_matrix[3].xyz
#     p_tail = tail.world_matrix[3].xyz
#     dir = glm.normalize(p_tail - p_head)
#     target = forward
#     axis = glm.normalize(glm.cross(dir, target))
#     dot = glm.dot(dir, target)
#     r = glm.angleAxis(math.acos(dot), axis)
#     head.pose = Transform.from_rotation(r)


def make_tpose(root: Node):

    upper_arm = root.find(lambda node: node.humanoid_bone ==
                          HumanoidBone.leftUpperArm)
    if not upper_arm:
        return

    for node, _ in upper_arm.traverse_node_and_parent():
        if not node.humanoid_bone:
            continue
        # if node.humanoid_bone == HumanoidBone.leftHand:
        #     continue
        if node.humanoid_tail:
            root.calc_skinning(glm.mat4())
            mod(node, node.humanoid_tail, glm.vec3(1, 0, 0))

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


class TPose(Motion):
    def __init__(self, model_name: str, root: Node) -> None:
        super().__init__(f'TPose [{model_name}]')
        self.humanoid_bones = set([node.humanoid_bone for node,
                                   _ in root.traverse_node_and_parent() if node.humanoid_bone])
        make_tpose(root)
        self.pose = Pose(self.name)
        for node, _ in root.traverse_node_and_parent():
            if node.pose:
                self.pose.bones.append(
                    BonePose(node.name, node.humanoid_bone, node.pose))
        root.clear_pose()
        root.calc_skinning(glm.mat4())

    def get_humanbones(self) -> Set[HumanoidBone]:
        return self.humanoid_bones

    def get_current_pose(self) -> Pose:
        return self.pose
