from typing import Tuple
from enum import Enum, Flag, auto
import glm


ZERO = glm.vec3(0, 0, 0)
UP = glm.vec3(0, 1, 0)
DOWN = glm.vec3(0, -1, 0)
FORWARD = glm.vec3(0, 0, 1)
BACK = glm.vec3(0, 0, -1)
LEFT = glm.vec3(1, 0, 0)
RIGHT = glm.vec3(-1, 0, 0)


class BoneFlags(Flag):
    Center = auto()
    Left = auto()
    Right = auto()
    FingerThumbnail = auto()
    FingerIndex = auto()
    FingerMiddle = auto()
    FingerRing = auto()
    FingerLittle = auto()


class BoneBase(Enum):
    unknown = auto()
    hips = auto()
    spine = auto()
    chest = auto()
    neck = auto()
    head = auto()
    shoulder = auto()
    upperArm = auto()
    lowerArm = auto()
    hand = auto()
    upperLeg = auto()
    lowerLeg = auto()
    foot = auto()
    toes = auto()
    finger_1 = auto()
    finger_2 = auto()
    finger_3 = auto()
    endSite = auto()


class HumanoidBone(Enum):
    unknown = (BoneBase.unknown, BoneFlags.Center, ZERO, ZERO)
    # trunk:
    hips = (BoneBase.hips, BoneFlags.Center, UP, FORWARD)
    spine = (BoneBase.spine, BoneFlags.Center, UP, FORWARD)
    chest = (BoneBase.chest, BoneFlags.Center, UP, FORWARD)
    neck = (BoneBase.neck, BoneFlags.Center, UP, FORWARD)
    head = (BoneBase.head, BoneFlags.Center, UP, FORWARD)
    # このライブラリでは使わない
    # upperChest = auto()
    # leftEye = auto()
    # rightEye = auto()
    # jaw = auto()
    # arms:
    leftShoulder = (BoneBase.shoulder, BoneFlags.Left, LEFT, FORWARD)
    leftUpperArm = (BoneBase.upperArm, BoneFlags.Left, LEFT, FORWARD)
    leftLowerArm = (BoneBase.lowerArm, BoneFlags.Left, LEFT, FORWARD)
    leftHand = (BoneBase.hand, BoneFlags.Left, LEFT, DOWN)
    rightShoulder = (BoneBase.shoulder, BoneFlags.Right, RIGHT, FORWARD)
    rightUpperArm = (BoneBase.upperArm, BoneFlags.Right, RIGHT, FORWARD)
    rightLowerArm = (BoneBase.lowerArm, BoneFlags.Right, RIGHT, FORWARD)
    rightHand = (BoneBase.hand, BoneFlags.Right, RIGHT, DOWN)
    # legs: foot の endSite は踵
    leftUpperLeg = (BoneBase.upperLeg, BoneFlags.Left, DOWN, BACK)
    leftLowerLeg = (BoneBase.lowerLeg, BoneFlags.Left, DOWN, BACK)
    leftFoot = (BoneBase.foot, BoneFlags.Left, DOWN, BACK)
    rightUpperLeg = (BoneBase.upperLeg, BoneFlags.Right, DOWN, BACK)
    rightLowerLeg = (BoneBase.lowerLeg, BoneFlags.Right, DOWN, BACK)
    rightFoot = (BoneBase.foot, BoneFlags.Right, DOWN, BACK)
    # toes: 手指と同じで非連続
    leftToes = (BoneBase.toes, BoneFlags.Left, FORWARD, DOWN)
    rightToes = (BoneBase.toes, BoneFlags.Right, FORWARD, DOWN)
    # 各指３関節だが、親指とその他で構成が違う
    # [親指]
    # 中手骨(metacarpal) - 指節骨(proximal, distal),
    # [人指,中,薬,小]
    # 指節骨(proximal, intermediate, distal)
    leftThumbProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerThumbnail, LEFT, BACK)
    leftThumbIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerThumbnail, LEFT, BACK)
    leftThumbDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerThumbnail, LEFT, BACK)
    leftIndexProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerIndex, LEFT, DOWN)
    leftIndexIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerIndex, LEFT, DOWN)
    leftIndexDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerIndex, LEFT, DOWN)
    leftMiddleProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerMiddle, LEFT, DOWN)
    leftMiddleIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerMiddle, LEFT, DOWN)
    leftMiddleDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerMiddle, LEFT, DOWN)
    leftRingProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerRing, LEFT, DOWN)
    leftRingIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerRing, LEFT, DOWN)
    leftRingDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerRing, LEFT, DOWN)
    leftLittleProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerLittle, LEFT, DOWN)
    leftLittleIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerLittle, LEFT, DOWN)
    leftLittleDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerLittle, LEFT, DOWN)
    #
    rightThumbProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerThumbnail, RIGHT, BACK)
    rightThumbIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerThumbnail, RIGHT, BACK)
    rightThumbDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerThumbnail, RIGHT, BACK)
    rightIndexProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerIndex, RIGHT, DOWN)
    rightIndexIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerIndex, RIGHT, DOWN)
    rightIndexDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerIndex, RIGHT, DOWN)
    rightMiddleProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerMiddle, RIGHT, DOWN)
    rightMiddleIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerMiddle, RIGHT, DOWN)
    rightMiddleDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerMiddle, RIGHT, DOWN)
    rightRingProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerRing, RIGHT, DOWN)
    rightRingIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerRing, RIGHT, DOWN)
    rightRingDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerRing, RIGHT, DOWN)
    rightLittleProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerLittle, RIGHT, DOWN)
    rightLittleIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerLittle, RIGHT, DOWN)
    rightLittleDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerLittle, RIGHT, DOWN)
    # bvh
    endSite = (BoneBase.endSite, BoneFlags.Center, ZERO, ZERO)

    def __init__(self, base: BoneBase, flags: BoneFlags, world_dir: glm.vec3, world_second: glm.vec3):
        self.base = base
        self.flags = flags
        self.world_dir = world_dir
        self.world_second = world_second

    def is_enable(self) -> bool:
        if self in (HumanoidBone.unknown, HumanoidBone.endSite):
            return False
        return True

    def is_finger(self):
        return self.base in (BoneBase.finger_1, BoneBase.finger_2, BoneBase.finger_3)

    @staticmethod
    def baseflag(base: BoneBase, flags: BoneFlags) -> 'HumanoidBone':
        for bone in HumanoidBone:
            if bone.base == base and bone.flags == flags:
                return bone
        raise KeyError(f'({base}, {flags}) not found')

    def get_tail(self) -> 'HumanoidBone':
        if not self.is_enable():
            raise RuntimeError(f'{self} has no tail')
        return TAIL_MAP[self]


TAIL_MAP = {
    # trunk
    HumanoidBone.hips: HumanoidBone.spine,
    HumanoidBone.spine: HumanoidBone.chest,
    HumanoidBone.chest: HumanoidBone.neck,
    HumanoidBone.neck: HumanoidBone.head,
    HumanoidBone.head: HumanoidBone.endSite,
    # left
    HumanoidBone.leftUpperLeg: HumanoidBone.leftLowerLeg,
    HumanoidBone.leftLowerLeg: HumanoidBone.leftFoot,
    HumanoidBone.leftFoot: HumanoidBone.endSite,
    HumanoidBone.leftToes: HumanoidBone.endSite,
    HumanoidBone.leftShoulder: HumanoidBone.leftUpperArm,
    HumanoidBone.leftUpperArm: HumanoidBone.leftLowerArm,
    HumanoidBone.leftLowerArm: HumanoidBone.leftHand,
    HumanoidBone.leftHand: HumanoidBone.leftMiddleProximal,
    HumanoidBone.leftMiddleProximal: HumanoidBone.leftMiddleIntermediate,
    HumanoidBone.leftMiddleIntermediate: HumanoidBone.leftMiddleDistal,
    HumanoidBone.leftMiddleDistal: HumanoidBone.endSite,
    HumanoidBone.leftThumbProximal: HumanoidBone.leftThumbIntermediate,
    HumanoidBone.leftThumbIntermediate: HumanoidBone.leftThumbDistal,
    HumanoidBone.leftThumbDistal: HumanoidBone.endSite,
    HumanoidBone.leftIndexProximal: HumanoidBone.leftIndexIntermediate,
    HumanoidBone.leftIndexIntermediate: HumanoidBone.leftIndexDistal,
    HumanoidBone.leftIndexDistal: HumanoidBone.endSite,
    HumanoidBone.leftRingProximal: HumanoidBone.leftRingIntermediate,
    HumanoidBone.leftRingIntermediate: HumanoidBone.leftRingDistal,
    HumanoidBone.leftRingDistal: HumanoidBone.endSite,
    HumanoidBone.leftLittleProximal: HumanoidBone.leftLittleIntermediate,
    HumanoidBone.leftLittleIntermediate: HumanoidBone.leftLittleDistal,
    HumanoidBone.leftLittleDistal: HumanoidBone.endSite,
    # right
    HumanoidBone.rightUpperLeg: HumanoidBone.rightLowerLeg,
    HumanoidBone.rightLowerLeg: HumanoidBone.rightFoot,
    HumanoidBone.rightFoot: HumanoidBone.endSite,
    HumanoidBone.rightToes: HumanoidBone.endSite,
    HumanoidBone.rightShoulder: HumanoidBone.rightUpperArm,
    HumanoidBone.rightUpperArm: HumanoidBone.rightLowerArm,
    HumanoidBone.rightLowerArm: HumanoidBone.rightHand,
    HumanoidBone.rightHand: HumanoidBone.rightMiddleProximal,
    HumanoidBone.rightMiddleProximal: HumanoidBone.rightMiddleIntermediate,
    HumanoidBone.rightMiddleIntermediate: HumanoidBone.rightMiddleDistal,
    HumanoidBone.rightMiddleDistal: HumanoidBone.endSite,
    HumanoidBone.rightThumbProximal: HumanoidBone.rightThumbIntermediate,
    HumanoidBone.rightThumbIntermediate: HumanoidBone.rightThumbDistal,
    HumanoidBone.rightThumbDistal: HumanoidBone.endSite,
    HumanoidBone.rightIndexProximal: HumanoidBone.rightIndexIntermediate,
    HumanoidBone.rightIndexIntermediate: HumanoidBone.rightIndexDistal,
    HumanoidBone.rightIndexDistal: HumanoidBone.endSite,
    HumanoidBone.rightRingProximal: HumanoidBone.rightRingIntermediate,
    HumanoidBone.rightRingIntermediate: HumanoidBone.rightRingDistal,
    HumanoidBone.rightRingDistal: HumanoidBone.endSite,
    HumanoidBone.rightLittleProximal: HumanoidBone.rightLittleIntermediate,
    HumanoidBone.rightLittleIntermediate: HumanoidBone.rightLittleDistal,
    HumanoidBone.rightLittleDistal: HumanoidBone.endSite,
}
