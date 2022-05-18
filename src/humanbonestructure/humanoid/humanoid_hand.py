from typing import NamedTuple, List, Optional, TypeAlias, Dict, Union
import glm
from ..scene.node import Node
from .humanoid_bones import HumanoidBone, BoneBase, BoneFlags
from .transform import Transform


NodeMap: TypeAlias = Dict[HumanoidBone, Node]


class HumanoidFinger(NamedTuple):
    position: glm.vec3
    finger1: float
    finger2: float
    finger3: float


class HumanoidHand(NamedTuple):
    left_right: BoneFlags
    middle: Union[float, HumanoidFinger]
    thumbnail: Optional[HumanoidFinger] = None
    index: Optional[HumanoidFinger] = None
    ring: Optional[HumanoidFinger] = None
    little: Optional[HumanoidFinger] = None

    @staticmethod
    def create_default(left_right: BoneFlags):
        if left_right == BoneFlags.Left:
            f = 1
        elif left_right == BoneFlags.Right:
            f = -1
        else:
            raise Exception()
        return HumanoidHand(
            left_right,
            thumbnail=HumanoidFinger(
                glm.vec3(f*0.02, -0.01, 0.03), 0.04, 0.02, 0.015),
            index=HumanoidFinger(
                glm.vec3(f*0.07, 0, 0.015), 0.04, 0.02, 0.015),
            middle=HumanoidFinger(glm.vec3(f*0.08, 0, 0), 0.04, 0.02, 0.015),
            ring=HumanoidFinger(
                glm.vec3(f*0.07, 0, -0.015), 0.04, 0.02, 0.015),
            little=HumanoidFinger(
                glm.vec3(f*0.06, 0, -0.03), 0.04, 0.02, 0.015),
        )

    @ staticmethod
    def from_node_map(node_map: NodeMap, left_right: BoneFlags) -> Optional['HumanoidHand']:
        pass

    def to_node(self, hand: Node):
        prefix = self.left_right.name

        def bone(base: BoneBase, flag: BoneFlags) -> HumanoidBone:
            return HumanoidBone.baseflag(base, self.left_right | flag)

        t = Transform.from_translation

        if self.left_right == BoneFlags.Left:
            d = glm.vec3(1, 0, 0)
        elif self.left_right == BoneFlags.Right:
            d = glm.vec3(-1, 0, 0)
        else:
            raise Exception('left or right')

        if isinstance(self.thumbnail, HumanoidFinger):
            hand.add_child(Node(f'{prefix}ThumbProximal', t(self.thumbnail.position), bone(BoneBase.finger_1, BoneFlags.FingerThumbnail), children=[
                Node(f'{prefix}ThumbIntermediate', t(d*self.thumbnail.finger1), bone(BoneBase.finger_2, BoneFlags.FingerThumbnail), children=[
                    Node(f'{prefix}ThumbDistal', t(d*self.thumbnail.finger2), bone(BoneBase.finger_3, BoneFlags.FingerThumbnail), children=[
                        Node(f'{prefix}ThumbEnd', t(
                            d*self.thumbnail.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))

        if isinstance(self.index, HumanoidFinger):
            hand.add_child(Node(f'{prefix}IndexProximal', t(self.index.position), bone(BoneBase.finger_1, BoneFlags.FingerIndex), children=[
                Node(f'{prefix}IndexIntermediate', t(d*self.index.finger1), bone(BoneBase.finger_2, BoneFlags.FingerIndex), children=[
                    Node(f'{prefix}IndexDistal', t(d*self.index.finger2), bone(BoneBase.finger_3, BoneFlags.FingerIndex), children=[
                        Node(f'{prefix}IndexEnd', t(
                            d*self.index.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))

        if isinstance(self.middle, HumanoidFinger):
            hand.add_child(Node(f'{prefix}MiddleProximal', t(self.middle.position), bone(BoneBase.finger_1, BoneFlags.FingerMiddle), children=[
                Node(f'{prefix}MiddleIntermediate', t(d*self.middle.finger1), bone(BoneBase.finger_2, BoneFlags.FingerMiddle), children=[
                    Node(f'{prefix}MiddleDistal', t(d*self.middle.finger2), bone(BoneBase.finger_3, BoneFlags.FingerMiddle), children=[
                        Node(f'{prefix}MiddleEnd', t(
                            d*self.middle.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))

        if isinstance(self.ring, HumanoidFinger):
            hand.add_child(Node(f'{prefix}RingProximal', t(self.ring.position), bone(BoneBase.finger_1, BoneFlags.FingerRing), children=[
                Node(f'{prefix}RingIntermediate', t(d*self.ring.finger1), bone(BoneBase.finger_2, BoneFlags.FingerRing), children=[
                    Node(f'{prefix}RingDistal', t(d*self.ring.finger2), bone(BoneBase.finger_3, BoneFlags.FingerRing), children=[
                        Node(f'{prefix}RingEnd', t(
                            d*self.ring.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))

        if isinstance(self.little, HumanoidFinger):
            hand.add_child(Node(f'{prefix}LittleProximal', t(self.little.position), bone(BoneBase.finger_1, BoneFlags.FingerLittle), children=[
                Node(f'{prefix}LittleIntermediate', t(d*self.little.finger1), bone(BoneBase.finger_2, BoneFlags.FingerLittle), children=[
                    Node(f'{prefix}LittleDistal', t(d*self.little.finger2), bone(BoneBase.finger_3, BoneFlags.FingerLittle), children=[
                        Node(f'{prefix}LittleEnd', t(
                            d*self.little.finger3), HumanoidBone.endSite)
                    ])
                ])
            ]))
