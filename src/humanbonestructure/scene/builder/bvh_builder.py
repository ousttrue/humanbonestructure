from typing import Optional
import logging
import glm
from ..node import Node
from ...formats import bvh_parser
from ...formats.transform import Transform
from ...formats.humanoid_bones import HumanoidBone

LOGGER = logging.getLogger(__name__)


def build(bvh: bvh_parser.Bvh) -> Node:

    count = [0]

    def get_counter():
        value = count[0]
        count[0] += 1
        return value

    def build(src: bvh_parser.Node, parent: Optional[Node] = None):
        index = get_counter()
        node = Node(
            src.name if src.name else f'bone#{index}', Transform.from_translation(
                src.offset),
            humanoid_bone=src.humanoid_bone)

        for child in src.children:
            child_node = build(child, node)
            node.add_child(child_node)

        return node

    hips = build(bvh.root)

    hips.initialize(glm.mat4())
    hips.calc_skinning(glm.mat4())

    # hips が root なので root を追加
    root = Node('__root__', Transform.identity())
    root.add_child(hips)

    return hips
