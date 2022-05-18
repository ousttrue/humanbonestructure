from typing import NamedTuple, List, Optional, TypeAlias, Dict, Union
import glm
from ..scene.node import Node
from .humanoid_bones import HumanoidBone, BoneFlags
from .transform import Transform


NodeMap: TypeAlias = Dict[HumanoidBone, Node]


class HumanoidFinger(NamedTuple):
    position: glm.vec3
    finger1: float
    finger2: float
    finger3: float


class HumanoidLeftHand(NamedTuple):
    middle: Union[float, HumanoidFinger]
    thumbnail: Optional[HumanoidFinger] = None
    index: Optional[HumanoidFinger] = None
    ring: Optional[HumanoidFinger] = None
    little: Optional[HumanoidFinger] = None

    @staticmethod
    def create_default():
        return HumanoidLeftHand(
            thumbnail=HumanoidFinger(
                glm.vec3(0.02, -0.01, 0.03), 0.04, 0.02, 0.015),
            index=HumanoidFinger(glm.vec3(0.07, 0, 0.015), 0.04, 0.02, 0.015),
            middle=HumanoidFinger(glm.vec3(0.08, 0, 0), 0.04, 0.02, 0.015),
            ring=HumanoidFinger(glm.vec3(0.07, 0, -0.015), 0.04, 0.02, 0.015),
            little=HumanoidFinger(glm.vec3(0.06, 0, -0.03), 0.04, 0.02, 0.015),
        )

    @ staticmethod
    def from_node_map(node_map: NodeMap, left_right: BoneFlags) -> Optional['HumanoidLeftHand']:
        pass

    def to_node(self, hand: Node):
        d = glm.vec3(1, 0, 0)
        if isinstance(self.thumbnail, HumanoidFinger):
            hand.add_child(Node('leftThumbProximal', Transform.from_translation(self.thumbnail.position), HumanoidBone.leftThumbProximal, children=[
                Node('leftThumbIntermediate', Transform.from_translation(d*self.thumbnail.finger1), HumanoidBone.leftThumbIntermediate, children=[
                    Node('leftThumbDistal', Transform.from_translation(d*self.thumbnail.finger2), HumanoidBone.leftThumbDistal, children=[
                        Node('leftThumbEnd', Transform.from_translation(
                            d*self.thumbnail.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))

        if isinstance(self.index, HumanoidFinger):
            hand.add_child(Node('leftIndexProximal', Transform.from_translation(self.index.position), HumanoidBone.leftIndexProximal, children=[
                Node('leftIndexIntermediate', Transform.from_translation(d*self.index.finger1), HumanoidBone.leftIndexIntermediate, children=[
                    Node('leftIndexDistal', Transform.from_translation(d*self.index.finger2), HumanoidBone.leftIndexDistal, children=[
                        Node('leftIndexEnd', Transform.from_translation(
                            d*self.index.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))

        if isinstance(self.middle, HumanoidFinger):
            hand.add_child(Node('leftMiddleProximal', Transform.from_translation(self.middle.position), HumanoidBone.leftMiddleProximal, children=[
                Node('leftMiddleIntermediate', Transform.from_translation(d*self.middle.finger1), HumanoidBone.leftMiddleIntermediate, children=[
                    Node('leftMiddleDistal', Transform.from_translation(d*self.middle.finger2), HumanoidBone.leftMiddleDistal, children=[
                        Node('leftMiddleEnd', Transform.from_translation(
                            d*self.middle.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))

        if isinstance(self.ring, HumanoidFinger):
            hand.add_child(Node('leftRingProximal', Transform.from_translation(self.ring.position), HumanoidBone.leftRingProximal, children=[
                Node('leftRingIntermediate', Transform.from_translation(d*self.ring.finger1), HumanoidBone.leftRingIntermediate, children=[
                    Node('leftRingDistal', Transform.from_translation(d*self.ring.finger2), HumanoidBone.leftRingDistal, children=[
                        Node('leftRingEnd', Transform.from_translation(
                            d*self.ring.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))

        if isinstance(self.little, HumanoidFinger):
            hand.add_child(Node('leftLittleProximal', Transform.from_translation(self.little.position), HumanoidBone.leftLittleProximal, children=[
                Node('leftLittleIntermediate', Transform.from_translation(d*self.little.finger1), HumanoidBone.leftLittleIntermediate, children=[
                    Node('leftLittleDistal', Transform.from_translation(d*self.little.finger2), HumanoidBone.leftLittleDistal, children=[
                        Node('leftLittleEnd', Transform.from_translation(
                            d*self.little.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))


class HumanoidRightHand(NamedTuple):
    middle: Union[float, HumanoidFinger]
    thumbnail: Optional[HumanoidFinger] = None
    index: Optional[HumanoidFinger] = None
    ring: Optional[HumanoidFinger] = None
    little: Optional[HumanoidFinger] = None
