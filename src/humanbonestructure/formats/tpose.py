from typing import Dict, Set
import glm
from ..scene.node import Node
from .humanoid_bones import HumanoidBone, HUMANOIDBONE_WORLD_AXIS
from .transform import Transform
from .pose import Motion, Pose, BonePose


def force_axis(head: Node, tail: Node, to: glm.vec3):
    local_matrix = glm.inverse(head.world_matrix) * tail.world_matrix
    src = glm.normalize(local_matrix[3].xyz)
    to = glm.inverse(glm.quat(head.world_matrix)) * to
    axis = glm.normalize(glm.cross(src, to))
    cos = glm.dot(src, to)
    r = glm.angleAxis(glm.acos(cos), axis)
    head.pose = Transform.from_rotation(r)
    parent_matrix = head.parent.world_matrix if head.parent else glm.mat4()
    head.calc_world_matrix(parent_matrix)


def make_tpose(root: Node, *, is_inverted_pelvis=False):

    for node, _ in root.traverse_node_and_parent():
        if node.humanoid_bone.is_enable() and node.humanoid_tail:
            root.calc_world_matrix(glm.mat4())
            if node.humanoid_bone == HumanoidBone.hips and is_inverted_pelvis:
                dir = (0, -1, 0)
            else:
                dir = HUMANOIDBONE_WORLD_AXIS[node.humanoid_bone]
            force_axis(node, node.humanoid_tail, glm.vec3(*dir))

    root.calc_world_matrix(glm.mat4())


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


def pose_to_delta(root: Node):
    for node, parent in root.traverse_node_and_parent():
        r = glm.quat()
        if node.pose:
            r = node.pose.rotation
        node.delta = r
        node.pose = None


def local_axis_fit_world(root: Node):
    for node, parent in root.traverse_node_and_parent():
        node.local_axis = glm.inverse(
            glm.quat(node.world_matrix))  # * glm.mat4

    root.calc_world_matrix(glm.mat4())


class TPose(Motion):
    def __init__(self, model_name: str, root: Node) -> None:
        super().__init__(f'TPose [{model_name}]')
        self.humanoid_bones = set([node.humanoid_bone for node,
                                   _ in root.traverse_node_and_parent() if node.humanoid_bone.is_enable()])
        make_tpose(root)
        self.pose = Pose(self.name)
        for node, _ in root.traverse_node_and_parent():
            if node.pose:
                self.pose.bones.append(
                    BonePose(node.name, node.humanoid_bone, node.pose))
        root.clear_pose()
        root.calc_world_matrix(glm.mat4())

    def get_humanbones(self) -> Set[HumanoidBone]:
        return self.humanoid_bones

    def get_current_pose(self) -> Pose:
        return self.pose
