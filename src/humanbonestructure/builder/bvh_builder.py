from typing import Optional, Dict
import logging
import glm
from ..formats.node import Node
from ..formats.bvh import bvh_parser
from ..formats.transform import Transform
from ..humanoid.humanoid_bones import HumanoidBone
from .hierarchy import Hierarchy

LOGGER = logging.getLogger(__name__)


def build(bvh: bvh_parser.Bvh) -> Hierarchy:

    node_humanoid_map: Dict[Node, HumanoidBone] = {}
    count = [0]

    def get_counter():
        value = count[0]
        count[0] += 1
        return value

    def build(src: bvh_parser.Node, parent: Optional[Node] = None):
        index = get_counter()
        node = Node(
            src.name if src.name else f'bone#{index}', Transform.from_translation(
                src.offset))
        node_humanoid_map[node] = src.humanoid_bone

        for child in src.children:
            if child.humanoid_bone==HumanoidBone.endSite:
                match src.humanoid_bone:
                    case HumanoidBone.leftHand:
                        # upgrade endsite
                        child.humanoid_bone = HumanoidBone.leftMiddleProximal
                    case HumanoidBone.rightHand:
                        # upgrade endsite
                        child.humanoid_bone = HumanoidBone.rightMiddleProximal
            child_node = build(child, node)
            node.add_child(child_node)

        return node

    hips = build(bvh.root)
    hips.calc_bind_matrix(glm.mat4())
    hips.calc_world_matrix(glm.mat4())

    # hips が root なので root を追加
    root = Node('__root__', Transform.identity())
    root.add_child(hips)

    return Hierarchy(root, node_humanoid_map)
