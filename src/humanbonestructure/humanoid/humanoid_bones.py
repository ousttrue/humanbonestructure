from typing import Tuple, NamedTuple, Optional, Dict
from enum import Enum, auto
import glm


class LeftRight(Enum):
    Center = 0
    Left = 1
    Right = 2


class HumanoidBone(Enum):
    unknown = auto()
    # trunk:
    hips = auto()
    spine = auto()
    chest = auto()
    neck = auto()
    head = auto()
    # このライブラリでは使わない
    # upperChest = auto()
    # leftEye = auto()
    # rightEye = auto()
    # jaw = auto()
    # arms:
    leftShoulder = auto()
    leftUpperArm = auto()
    leftLowerArm = auto()
    leftHand = auto()
    rightShoulder = auto()
    rightUpperArm = auto()
    rightLowerArm = auto()
    rightHand = auto()
    # legs: foot の endSite は踵
    leftUpperLeg = auto()
    leftLowerLeg = auto()
    leftFoot = auto()
    rightUpperLeg = auto()
    rightLowerLeg = auto()
    rightFoot = auto()
    # toes: 手指と同じで非連続
    leftToes = auto()
    rightToes = auto()
    # 各指３関節だが、親指とその他で構成が違う
    # [親指]
    # 中手骨(metacarpal) - 指節骨(proximal, distal),
    # [人指,中,薬,小]
    # 指節骨(proximal, intermediate, distal)
    leftThumbProximal = auto()
    leftThumbIntermediate = auto()
    leftThumbDistal = auto()
    leftIndexProximal = auto()
    leftIndexIntermediate = auto()
    leftIndexDistal = auto()
    leftMiddleProximal = auto()
    leftMiddleIntermediate = auto()
    leftMiddleDistal = auto()
    leftRingProximal = auto()
    leftRingIntermediate = auto()
    leftRingDistal = auto()
    leftLittleProximal = auto()
    leftLittleIntermediate = auto()
    leftLittleDistal = auto()
    rightThumbProximal = auto()
    rightThumbIntermediate = auto()
    rightThumbDistal = auto()
    rightIndexProximal = auto()
    rightIndexIntermediate = auto()
    rightIndexDistal = auto()
    rightMiddleProximal = auto()
    rightMiddleIntermediate = auto()
    rightMiddleDistal = auto()
    rightRingProximal = auto()
    rightRingIntermediate = auto()
    rightRingDistal = auto()
    rightLittleProximal = auto()
    rightLittleIntermediate = auto()
    rightLittleDistal = auto()
    # bvh
    endSite = auto()

    def is_enable(self) -> bool:
        return self != HumanoidBone.unknown and self != HumanoidBone.endSite

    def get_world_axis(self) -> Tuple[float, float, float]:
        return HUMANOIDBONE_WORLD_AXIS[self]

    def is_finger(self):
        return self in FINGER_SET


UP = (0, 1, 0)
DOWN = (0, -1, 0)
FORWARD = (0, 0, 1)
LEFT = (1, 0, 0)
RIGHT = (-1, 0, 0)

FINGER_SET = set([
    HumanoidBone.leftThumbProximal,
    HumanoidBone.leftThumbIntermediate,
    HumanoidBone.leftThumbDistal,
    HumanoidBone.leftIndexProximal,
    HumanoidBone.leftIndexIntermediate,
    HumanoidBone.leftIndexDistal,
    HumanoidBone.leftMiddleProximal,
    HumanoidBone.leftMiddleIntermediate,
    HumanoidBone.leftMiddleDistal,
    HumanoidBone.leftRingProximal,
    HumanoidBone.leftRingIntermediate,
    HumanoidBone.leftRingDistal,
    HumanoidBone.leftLittleProximal,
    HumanoidBone.leftLittleIntermediate,
    HumanoidBone.leftLittleDistal,
    HumanoidBone.rightThumbProximal,
    HumanoidBone.rightThumbIntermediate,
    HumanoidBone.rightThumbDistal,
    HumanoidBone.rightIndexProximal,
    HumanoidBone.rightIndexIntermediate,
    HumanoidBone.rightIndexDistal,
    HumanoidBone.rightMiddleProximal,
    HumanoidBone.rightMiddleIntermediate,
    HumanoidBone.rightMiddleDistal,
    HumanoidBone.rightRingProximal,
    HumanoidBone.rightRingIntermediate,
    HumanoidBone.rightRingDistal,
    HumanoidBone.rightLittleProximal,
    HumanoidBone.rightLittleIntermediate,
    HumanoidBone.rightLittleDistal,
])

HUMANOIDBONE_WORLD_AXIS = {
    HumanoidBone.hips: UP,
    HumanoidBone.spine: UP,
    HumanoidBone.chest: UP,
    HumanoidBone.neck: UP,
    HumanoidBone.head: UP,
    HumanoidBone.leftUpperLeg: DOWN,
    HumanoidBone.leftLowerLeg: DOWN,
    HumanoidBone.leftFoot: DOWN,
    HumanoidBone.rightUpperLeg: DOWN,
    HumanoidBone.rightLowerLeg: DOWN,
    HumanoidBone.rightFoot: DOWN,
    HumanoidBone.leftShoulder: LEFT,
    HumanoidBone.leftUpperArm: LEFT,
    HumanoidBone.leftLowerArm: LEFT,
    HumanoidBone.leftHand: LEFT,
    HumanoidBone.rightShoulder: RIGHT,
    HumanoidBone.rightUpperArm: RIGHT,
    HumanoidBone.rightLowerArm: RIGHT,
    HumanoidBone.rightHand: RIGHT,
    #
    HumanoidBone.leftToes: FORWARD,
    HumanoidBone.rightToes: FORWARD,
    #
    HumanoidBone.leftThumbProximal: LEFT,
    HumanoidBone.leftThumbIntermediate: LEFT,
    HumanoidBone.leftThumbDistal: LEFT,
    HumanoidBone.leftIndexProximal: LEFT,
    HumanoidBone.leftIndexIntermediate: LEFT,
    HumanoidBone.leftIndexDistal: LEFT,
    HumanoidBone.leftMiddleProximal: LEFT,
    HumanoidBone.leftMiddleIntermediate: LEFT,
    HumanoidBone.leftMiddleDistal: LEFT,
    HumanoidBone.leftRingProximal: LEFT,
    HumanoidBone.leftRingIntermediate: LEFT,
    HumanoidBone.leftRingDistal: LEFT,
    HumanoidBone.leftLittleProximal: LEFT,
    HumanoidBone.leftLittleIntermediate: LEFT,
    HumanoidBone.leftLittleDistal: LEFT,
    HumanoidBone.rightThumbProximal: RIGHT,
    HumanoidBone.rightThumbIntermediate: RIGHT,
    HumanoidBone.rightThumbDistal: RIGHT,
    HumanoidBone.rightIndexProximal: RIGHT,
    HumanoidBone.rightIndexIntermediate: RIGHT,
    HumanoidBone.rightIndexDistal: RIGHT,
    HumanoidBone.rightMiddleProximal: RIGHT,
    HumanoidBone.rightMiddleIntermediate: RIGHT,
    HumanoidBone.rightMiddleDistal: RIGHT,
    HumanoidBone.rightRingProximal: RIGHT,
    HumanoidBone.rightRingIntermediate: RIGHT,
    HumanoidBone.rightRingDistal: RIGHT,
    HumanoidBone.rightLittleProximal: RIGHT,
    HumanoidBone.rightLittleIntermediate: RIGHT,
    HumanoidBone.rightLittleDistal: RIGHT,
}
