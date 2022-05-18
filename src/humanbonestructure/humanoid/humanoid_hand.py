from typing import NamedTuple, List, Optional, TypeAlias, Dict, Union
import glm
from ..scene.node import Node
from .humanoid_bones import HumanoidBone, LeftRight, Fingers, UP
from .transform import Transform


NodeMap: TypeAlias = Dict[HumanoidBone, Node]


class HumanoidFinger(NamedTuple):
    position: glm.vec3
    finger1: float
    finger2: float
    finger3: float

    @ staticmethod
    def from_node_map(node_map: NodeMap, left_right: LeftRight, fingers: Fingers) -> Optional['HumanoidFinger']:
        pass


class HumanoidLeftHand(NamedTuple):
    middle: Union[float, HumanoidFinger]
    thumbnail: Optional[HumanoidFinger] = None
    index: Optional[HumanoidFinger] = None
    ring: Optional[HumanoidFinger] = None
    little: Optional[HumanoidFinger] = None

    @ staticmethod
    def from_node_map(node_map: NodeMap, left_right: LeftRight) -> Optional['HumanoidLeftHand']:
        pass

    def to_node(self, lowerArmLength: float) -> Node:
        d = glm.vec3(0, 1, 0)

        hand = Node('leftHand', Transform.from_translation(d*lowerArmLength))
        return hand


class HumanoidRightHand(NamedTuple):
    middle: Union[float, HumanoidFinger]
    thumbnail: Optional[HumanoidFinger] = None
    index: Optional[HumanoidFinger] = None
    ring: Optional[HumanoidFinger] = None
    little: Optional[HumanoidFinger] = None
