from typing import Tuple
from enum import Enum, Flag, auto
import glm


ZERO = glm.vec3(0, 0, 0)
UP = glm.vec3(0, 1, 0)
DOWN = glm.vec3(0, -1, 0)
FORWARD = glm.vec3(0, 0, 1)
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
    unknown = (BoneBase.unknown, BoneFlags.Center, ZERO)
    # trunk:
    hips = (BoneBase.hips, BoneFlags.Center, UP)
    spine = (BoneBase.spine, BoneFlags.Center, UP)
    chest = (BoneBase.chest, BoneFlags.Center, UP)
    neck = (BoneBase.neck, BoneFlags.Center, UP)
    head = (BoneBase.head, BoneFlags.Center, UP)
    # このライブラリでは使わない
    # upperChest = auto()
    # leftEye = auto()
    # rightEye = auto()
    # jaw = auto()
    # arms:
    leftShoulder = (BoneBase.shoulder, BoneFlags.Left, LEFT)
    leftUpperArm = (BoneBase.upperArm, BoneFlags.Left, LEFT)
    leftLowerArm = (BoneBase.lowerArm, BoneFlags.Left, LEFT)
    leftHand = (BoneBase.hand, BoneFlags.Left, LEFT)
    rightShoulder = (BoneBase.shoulder, BoneFlags.Right, LEFT)
    rightUpperArm = (BoneBase.upperArm, BoneFlags.Right, LEFT)
    rightLowerArm = (BoneBase.lowerArm, BoneFlags.Right, LEFT)
    rightHand = (BoneBase.hand, BoneFlags.Right, LEFT)
    # legs: foot の endSite は踵
    leftUpperLeg = (BoneBase.upperLeg, BoneFlags.Left, DOWN)
    leftLowerLeg = (BoneBase.lowerLeg, BoneFlags.Left, DOWN)
    leftFoot = (BoneBase.foot, BoneFlags.Left, DOWN)
    rightUpperLeg = (BoneBase.upperLeg, BoneFlags.Right, DOWN)
    rightLowerLeg = (BoneBase.lowerLeg, BoneFlags.Right, DOWN)
    rightFoot = (BoneBase.foot, BoneFlags.Right, DOWN)
    # toes: 手指と同じで非連続
    leftToes = (BoneBase.toes, BoneFlags.Left, FORWARD)
    rightToes = (BoneBase.toes, BoneFlags.Right, FORWARD)
    # 各指３関節だが、親指とその他で構成が違う
    # [親指]
    # 中手骨(metacarpal) - 指節骨(proximal, distal),
    # [人指,中,薬,小]
    # 指節骨(proximal, intermediate, distal)
    leftThumbProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerThumbnail, LEFT)
    leftThumbIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerThumbnail, LEFT)
    leftThumbDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerThumbnail, LEFT)
    leftIndexProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerIndex, LEFT)
    leftIndexIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerIndex, LEFT)
    leftIndexDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerIndex, LEFT)
    leftMiddleProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerMiddle, LEFT)
    leftMiddleIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerMiddle, LEFT)
    leftMiddleDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerMiddle, LEFT)
    leftRingProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerRing, LEFT)
    leftRingIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerRing, LEFT)
    leftRingDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerRing, LEFT)
    leftLittleProximal = (
        BoneBase.finger_1, BoneFlags.Left | BoneFlags.FingerLittle, LEFT)
    leftLittleIntermediate = (
        BoneBase.finger_2, BoneFlags.Left | BoneFlags.FingerLittle, LEFT)
    leftLittleDistal = (
        BoneBase.finger_3, BoneFlags.Left | BoneFlags.FingerLittle, LEFT)
    #
    rightThumbProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerThumbnail, RIGHT)
    rightThumbIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerThumbnail, RIGHT)
    rightThumbDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerThumbnail, RIGHT)
    rightIndexProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerIndex, RIGHT)
    rightIndexIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerIndex, RIGHT)
    rightIndexDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerIndex, RIGHT)
    rightMiddleProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerMiddle, RIGHT)
    rightMiddleIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerMiddle, RIGHT)
    rightMiddleDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerMiddle, RIGHT)
    rightRingProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerRing, RIGHT)
    rightRingIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerRing, RIGHT)
    rightRingDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerRing, RIGHT)
    rightLittleProximal = (
        BoneBase.finger_1, BoneFlags.Right | BoneFlags.FingerLittle, RIGHT)
    rightLittleIntermediate = (
        BoneBase.finger_2, BoneFlags.Right | BoneFlags.FingerLittle, RIGHT)
    rightLittleDistal = (
        BoneBase.finger_3, BoneFlags.Right | BoneFlags.FingerLittle, RIGHT)
    # bvh
    endSite = (BoneBase.endSite, BoneFlags.Center, ZERO)

    def __init__(self, base: BoneBase, flags: BoneFlags, world_dir: glm.vec3):
        self.base = base
        self.flags = flags
        self.world_dir = world_dir

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
