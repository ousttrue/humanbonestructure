from typing import Tuple, NamedTuple, Optional, Dict
from enum import Enum, auto


class LeftRight(Enum):
    Center = 0
    Left = 1
    Right = 2


class Fingers(Enum):
    NotFinger = 0
    Thumbnail = 1
    Index = 2
    Middle = 3
    Ring = 4
    Little = 5


class HumanoidBodyParts(Enum):
    Unknown = 0  # unknown / endsite
    Trunk = 1
    Legs = 2
    Arms = 3
    Toes = 4
    Fingers = 5


class HumanoidBoneClassification(NamedTuple):
    part: HumanoidBodyParts
    left_right: LeftRight
    finger: Fingers = Fingers.NotFinger


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

    def get_classification(self) -> HumanoidBoneClassification:
        return HUMANOIDBONE_PART_MAP[self]

    def get_world_axis(self) -> Tuple[float, float, float]:
        return HUMANOIDBONE_WORLD_AXIS[self]


HUMANOIDBONE_PART_MAP: Dict[HumanoidBone, HumanoidBoneClassification] = {
    # core: 19bones hips-spine-chest-neck-head + (shoulder-upper-lower-hand)xLR + (upper-lower-foot)xLR
    HumanoidBone.hips:  HumanoidBoneClassification(HumanoidBodyParts.Trunk, LeftRight.Center),
    HumanoidBone.spine: HumanoidBoneClassification(HumanoidBodyParts.Trunk, LeftRight.Center),
    HumanoidBone.chest: HumanoidBoneClassification(HumanoidBodyParts.Trunk, LeftRight.Center),
    HumanoidBone.neck: HumanoidBoneClassification(HumanoidBodyParts.Trunk, LeftRight.Center),
    HumanoidBone.head: HumanoidBoneClassification(HumanoidBodyParts.Trunk, LeftRight.Center),
    HumanoidBone.leftUpperLeg: HumanoidBoneClassification(HumanoidBodyParts.Legs, LeftRight.Left),
    HumanoidBone.leftLowerLeg: HumanoidBoneClassification(HumanoidBodyParts.Legs, LeftRight.Left),
    HumanoidBone.leftFoot: HumanoidBoneClassification(HumanoidBodyParts.Legs, LeftRight.Left),
    HumanoidBone.rightUpperLeg: HumanoidBoneClassification(HumanoidBodyParts.Legs, LeftRight.Right),
    HumanoidBone.rightLowerLeg: HumanoidBoneClassification(HumanoidBodyParts.Legs, LeftRight.Right),
    HumanoidBone.rightFoot: HumanoidBoneClassification(HumanoidBodyParts.Legs, LeftRight.Right),
    HumanoidBone.leftShoulder: HumanoidBoneClassification(HumanoidBodyParts.Arms, LeftRight.Left),
    HumanoidBone.leftUpperArm: HumanoidBoneClassification(HumanoidBodyParts.Arms, LeftRight.Left),
    HumanoidBone.leftLowerArm: HumanoidBoneClassification(HumanoidBodyParts.Arms, LeftRight.Left),
    HumanoidBone.leftHand: HumanoidBoneClassification(HumanoidBodyParts.Arms, LeftRight.Left),
    HumanoidBone.rightShoulder: HumanoidBoneClassification(HumanoidBodyParts.Arms, LeftRight.Right),
    HumanoidBone.rightUpperArm: HumanoidBoneClassification(HumanoidBodyParts.Arms, LeftRight.Right),
    HumanoidBone.rightLowerArm: HumanoidBoneClassification(HumanoidBodyParts.Arms, LeftRight.Right),
    HumanoidBone.rightHand: HumanoidBoneClassification(HumanoidBodyParts.Arms, LeftRight.Right),
    # toes: 2bones 1xLR
    HumanoidBone.leftToes: HumanoidBoneClassification(HumanoidBodyParts.Toes, LeftRight.Left),
    HumanoidBone.rightToes: HumanoidBoneClassification(HumanoidBodyParts.Toes, LeftRight.Right),
    # fingers: 30bones (1-2-3)x5xLR
    HumanoidBone.leftThumbProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Thumbnail),
    HumanoidBone.leftThumbIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Thumbnail),
    HumanoidBone.leftThumbDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Thumbnail),
    HumanoidBone.leftIndexProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Index),
    HumanoidBone.leftIndexIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Index),
    HumanoidBone.leftIndexDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Index),
    HumanoidBone.leftMiddleProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Middle),
    HumanoidBone.leftMiddleIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Middle),
    HumanoidBone.leftMiddleDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Middle),
    HumanoidBone.leftRingProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Ring),
    HumanoidBone.leftRingIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Ring),
    HumanoidBone.leftRingDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Ring),
    HumanoidBone.leftLittleProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Little),
    HumanoidBone.leftLittleIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Little),
    HumanoidBone.leftLittleDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Left, Fingers.Little),
    HumanoidBone.rightThumbProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Thumbnail),
    HumanoidBone.rightThumbIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Thumbnail),
    HumanoidBone.rightThumbDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Thumbnail),
    HumanoidBone.rightIndexProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Index),
    HumanoidBone.rightIndexIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Index),
    HumanoidBone.rightIndexDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Index),
    HumanoidBone.rightMiddleProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Middle),
    HumanoidBone.rightMiddleIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Middle),
    HumanoidBone.rightMiddleDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Middle),
    HumanoidBone.rightRingProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Ring),
    HumanoidBone.rightRingIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Ring),
    HumanoidBone.rightRingDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Ring),
    HumanoidBone.rightLittleProximal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Little),
    HumanoidBone.rightLittleIntermediate: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Little),
    HumanoidBone.rightLittleDistal: HumanoidBoneClassification(HumanoidBodyParts.Fingers, LeftRight.Right, Fingers.Little),
}

UP = (0, 1, 0)
DOWN = (0, -1, 0)
FORWARD = (0, 0, 1)
LEFT = (1, 0, 0)
RIGHT = (-1, 0, 0)

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
