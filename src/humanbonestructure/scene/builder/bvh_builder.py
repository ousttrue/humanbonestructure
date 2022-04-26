from typing import Optional
import logging
import glm
from ..node import Node
from ...formats import bvh_parser
from ...formats.transform import Transform
from ...formats.humanoid_bones import HumanoidBone

LOGGER = logging.getLogger(__name__)

HUMANOID_MAP = {
    'Hips': HumanoidBone.hips,
    'Spine': HumanoidBone.spine,
    'Spine1': HumanoidBone.chest,
    'Neck': HumanoidBone.neck,
    'Head': HumanoidBone.head,

    'LeftShoulder': HumanoidBone.leftShoulder,
    'LeftArm': HumanoidBone.leftUpperArm,
    'LeftForeArm': HumanoidBone.leftLowerArm,
    'LeftHand': HumanoidBone.leftHand,

    'RightShoulder': HumanoidBone.rightShoulder,
    'RightArm': HumanoidBone.rightUpperArm,
    'RightForeArm': HumanoidBone.rightLowerArm,
    'RightHand': HumanoidBone.rightHand,

    'LeftUpLeg': HumanoidBone.leftUpperLeg,
    'LeftLeg': HumanoidBone.leftLowerLeg,
    'LeftFoot': HumanoidBone.leftFoot,
    'LeftToeBase': HumanoidBone.leftToes,

    'RightUpLeg': HumanoidBone.rightUpperLeg,
    'RightLeg': HumanoidBone.rightLowerLeg,
    'RightFoot': HumanoidBone.rightFoot,
    'RightToeBase': HumanoidBone.rightToes,
}


def build(bvh: bvh_parser.Bvh) -> Node:

    count = [0]

    def get_counter():
        value = count[0]
        count[0] += 1
        return value

    def build(src: bvh_parser.Node, parent: Optional[Node] = None):
        index = get_counter()
        node = Node(
            index, src.name if src.name else f'bone#{index}', Transform.from_translation(src.offset))
        if src.name:
            node.humanoid_bone = HUMANOID_MAP.get(src.name)

        for child in src.children:
            child_node = build(child, node)
            node.add_child(child_node)

        return node

    hips = build(bvh.root)

    hips.initialize(glm.mat4())
    hips.calc_skinning(glm.mat4())
    hips_y = 0
    min_y = 0
    for node, _ in hips.traverse_node_and_parent():
        y = node.world_matrix[3].y
        if node.humanoid_bone == HumanoidBone.hips:
            hips_y = y
        if y < min_y:
            min_y = y

    hips_height = hips_y - min_y
    scale = 1
    if hips_height > 70 and hips_height < 100:
        # cm to meter
        scale = 0.01

    for node, _ in hips.traverse_node_and_parent():
        node.init_trs = node.init_trs._replace(
            translation=node.init_trs.translation * scale)

    # hips が root なので root を追加
    root = Node(-1, '__root__', Transform.identity())

    # 接地させる
    hips_pos = hips.init_trs.translation
    hips_pos.y = hips_height * scale
    hips.init_trs = hips.init_trs._replace(translation=hips_pos)

    root.add_child(hips)

    return hips
