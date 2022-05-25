from typing import NamedTuple, List, Optional, TypeAlias, Dict, Union
import glm
from ..formats.node import Node
from .humanoid_bones import HumanoidBone, BoneBase, BoneFlags
from ..formats.transform import Transform


NodeMap: TypeAlias = Dict[HumanoidBone, Node]


class HumanoidFinger(NamedTuple):
    position: glm.vec3
    finger1: float
    finger2: float
    finger3: float

    @staticmethod
    def create(position: glm.vec3, f: float, f1: float):
        f2 = f1 * 0.8
        f3 = f2 * 0.8
        return HumanoidFinger(glm.vec3(position.x * f, position.y, position.z), f1, f2, f3)


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
            thumbnail=HumanoidFinger.create(
                glm.vec3(0.03, -0.01, 0.02), f, 0.03),
            index=HumanoidFinger.create(glm.vec3(0.075, 0, 0.015), f, 0.03),
            middle=HumanoidFinger.create(glm.vec3(0.08, 0, 0), f, 0.03),
            ring=HumanoidFinger.create(glm.vec3(0.075, 0, -0.015), f, 0.03),
            little=HumanoidFinger.create(glm.vec3(0.07, 0, -0.03), f, 0.03),
        )

    @ staticmethod
    def from_node_map(node_map: NodeMap, left_right: BoneFlags) -> Optional['HumanoidHand']:
        match left_right:
            case BoneFlags.Left:
                hand = node_map[HumanoidBone.leftHand].world_matrix[3].xyz
                thumb1 = node_map[HumanoidBone.leftThumbProximal].world_matrix[3].xyz
                thumb2 = node_map[HumanoidBone.leftThumbIntermediate].world_matrix[3].xyz
                thumb3 = node_map[HumanoidBone.leftThumbDistal].world_matrix[3].xyz
                thumb_end = node_map[HumanoidBone.leftThumbDistal].humanoid_tail
                index1 = node_map[HumanoidBone.leftIndexProximal].world_matrix[3].xyz
                index2 = node_map[HumanoidBone.leftIndexIntermediate].world_matrix[3].xyz
                index3 = node_map[HumanoidBone.leftIndexDistal].world_matrix[3].xyz
                index_end = node_map[HumanoidBone.leftIndexDistal].humanoid_tail
                middle1 = node_map[HumanoidBone.leftMiddleProximal].world_matrix[3].xyz
                middle2 = node_map[HumanoidBone.leftMiddleIntermediate].world_matrix[3].xyz
                middle3 = node_map[HumanoidBone.leftMiddleDistal].world_matrix[3].xyz
                middle_end = node_map[HumanoidBone.leftMiddleDistal].humanoid_tail
                ring1 = node_map[HumanoidBone.leftRingProximal].world_matrix[3].xyz
                ring2 = node_map[HumanoidBone.leftRingIntermediate].world_matrix[3].xyz
                ring3 = node_map[HumanoidBone.leftRingDistal].world_matrix[3].xyz
                ring_end = node_map[HumanoidBone.leftRingDistal].humanoid_tail
                little1 = node_map[HumanoidBone.leftLittleProximal].world_matrix[3].xyz
                little2 = node_map[HumanoidBone.leftLittleIntermediate].world_matrix[3].xyz
                little3 = node_map[HumanoidBone.leftLittleDistal].world_matrix[3].xyz
                little_end = node_map[HumanoidBone.leftLittleDistal].humanoid_tail
            case BoneFlags.Right:
                hand = node_map[HumanoidBone.rightHand].world_matrix[3].xyz
                thumb1 = node_map[HumanoidBone.rightThumbProximal].world_matrix[3].xyz
                thumb2 = node_map[HumanoidBone.rightThumbIntermediate].world_matrix[3].xyz
                thumb3 = node_map[HumanoidBone.rightThumbDistal].world_matrix[3].xyz
                thumb_end = node_map[HumanoidBone.rightThumbDistal].humanoid_tail
                index1 = node_map[HumanoidBone.rightIndexProximal].world_matrix[3].xyz
                index2 = node_map[HumanoidBone.rightIndexIntermediate].world_matrix[3].xyz
                index3 = node_map[HumanoidBone.rightIndexDistal].world_matrix[3].xyz
                index_end = node_map[HumanoidBone.rightIndexDistal].humanoid_tail
                middle1 = node_map[HumanoidBone.rightMiddleProximal].world_matrix[3].xyz
                middle2 = node_map[HumanoidBone.rightMiddleIntermediate].world_matrix[3].xyz
                middle3 = node_map[HumanoidBone.rightMiddleDistal].world_matrix[3].xyz
                middle_end = node_map[HumanoidBone.rightMiddleDistal].humanoid_tail
                ring1 = node_map[HumanoidBone.rightRingProximal].world_matrix[3].xyz
                ring2 = node_map[HumanoidBone.rightRingIntermediate].world_matrix[3].xyz
                ring3 = node_map[HumanoidBone.rightRingDistal].world_matrix[3].xyz
                ring_end = node_map[HumanoidBone.rightRingDistal].humanoid_tail
                little1 = node_map[HumanoidBone.rightLittleProximal].world_matrix[3].xyz
                little2 = node_map[HumanoidBone.rightLittleIntermediate].world_matrix[3].xyz
                little3 = node_map[HumanoidBone.rightLittleDistal].world_matrix[3].xyz
                little_end = node_map[HumanoidBone.rightLittleDistal].humanoid_tail
            case _:
                raise RuntimeError()
        assert thumb_end
        assert index_end
        assert middle_end
        assert ring_end
        assert little_end
        return HumanoidHand(left_right,
                            thumbnail=HumanoidFinger(thumb1-hand,
                                                     glm.length(thumb2-thumb1), glm.length(thumb3-thumb2), glm.length(thumb_end.world_matrix[3].xyz-thumb3)),
                            index=HumanoidFinger(index1-hand,
                                                 glm.length(index2-index1), glm.length(index3-index2), glm.length(index_end.world_matrix[3].xyz-index3)),
                            middle=HumanoidFinger(middle1-hand,
                                                  glm.length(middle2-middle1), glm.length(middle3-middle2), glm.length(middle_end.world_matrix[3].xyz-middle3)),
                            ring=HumanoidFinger(ring1-hand,
                                                glm.length(ring2-ring1), glm.length(ring3-ring2), glm.length(ring_end.world_matrix[3].xyz-ring3)),
                            little=HumanoidFinger(little1-hand,
                                                  glm.length(little2-little1), glm.length(little3-little2), glm.length(little_end.world_matrix[3].xyz-little3)))

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
