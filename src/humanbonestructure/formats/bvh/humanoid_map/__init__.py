from typing import Dict, Set
from ..bvh_node import Node
from ...humanoid_bones import HumanoidBone


def keys_match_dict(keys: Set[str], dict: Dict[str, HumanoidBone]) -> bool:
    for k in dict.keys():
        if k not in keys:
            return False
    # dict に含まれる名前がすべて見つかれば OK
    return True


def assign(root: Node, dict: Dict[str, HumanoidBone]):
    for node in root.traverse():
        if node.name:
            humanoid_bone = dict.get(node.name)
            if humanoid_bone:
                node.humanoid_bone = humanoid_bone


def try_assign(root, keys, dict) -> bool:
    if keys_match_dict(keys, dict):
        assign(root, dict)
        return True
    return False


def resolve(root: Node) -> bool:
    keys = set(node.name for node in root.traverse() if node.name)

    from . import bandai_namco
    if try_assign(root, keys, bandai_namco.MAP):
        return True

    from . import cgspeed
    if try_assign(root, keys, cgspeed.MAP):
        return True

    from . import univrm
    if try_assign(root, keys, univrm.MAP):
        return True

    from . import liveanimation
    if try_assign(root, keys, liveanimation.MAP):
        return True

    return False
