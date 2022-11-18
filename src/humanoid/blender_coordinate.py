from typing import Dict
import glm
from .humanoid_bones import HumanoidBone

_LEFT = glm.vec4(1, 0, 0, 0)
_RIGHT = glm.vec4(-1, 0, 0, 0)
_UP = glm.vec4(0, 1, 0, 0)
_DOWN = glm.vec4(0, -1, 0, 0)
_FORWARD = glm.vec4(0, 0, 1, 0)
_BACK = glm.vec4(0, 0, -1, 0)
_ZERO_ONE = glm.vec4(0, 0, 0, 1)


TRUNK_COORDS = glm.mat4(
    _RIGHT,
    _UP,
    _FORWARD,
    _ZERO_ONE,
)

# left arm
LEFT_ARM_COORDS = glm.mat4(
    _DOWN,
    _LEFT,
    _FORWARD,
    _ZERO_ONE,
)
LEFT_HAND_COORDS = glm.mat4(
    _BACK,
    _LEFT,
    _DOWN,
    _ZERO_ONE,
)
LEFT_THUMB_COORDS = glm.mat4(
    _UP,
    _LEFT,
    _BACK,
    _ZERO_ONE,
)

# right arm
RIGHT_ARM_COORDS = glm.mat4(
    _UP,
    _RIGHT,
    _FORWARD,
    _ZERO_ONE,
)
RIGHT_HAND_COORDS = glm.mat4(
    _FORWARD,
    _RIGHT,
    _DOWN,
    _ZERO_ONE,
)
RIGHT_THUMB_COORDS = glm.mat4(
    _DOWN,
    _RIGHT,
    _BACK,
    _ZERO_ONE,
)

# leg
LEG_COORDS = glm.mat4(
    _LEFT,
    _DOWN,
    _BACK,
    _ZERO_ONE,
)

TOES_COORDS = glm.mat4(
    _LEFT,
    _FORWARD,
    _DOWN,
    _ZERO_ONE,
)

BONE_COORDS_MAP: Dict[HumanoidBone, glm.mat4] = {
    HumanoidBone.hips: TRUNK_COORDS,
    HumanoidBone.spine: TRUNK_COORDS,
    HumanoidBone.chest: TRUNK_COORDS,
    HumanoidBone.neck: TRUNK_COORDS,
    HumanoidBone.head: TRUNK_COORDS,
    HumanoidBone.leftShoulder: LEFT_ARM_COORDS,
    HumanoidBone.leftUpperArm: LEFT_ARM_COORDS,
    HumanoidBone.leftLowerArm: LEFT_ARM_COORDS,
    HumanoidBone.leftHand: LEFT_HAND_COORDS,
    HumanoidBone.rightShoulder: RIGHT_ARM_COORDS,
    HumanoidBone.rightUpperArm: RIGHT_ARM_COORDS,
    HumanoidBone.rightLowerArm: RIGHT_ARM_COORDS,
    HumanoidBone.rightHand: RIGHT_HAND_COORDS,
    HumanoidBone.leftUpperLeg: LEG_COORDS,
    HumanoidBone.leftLowerLeg: LEG_COORDS,
    HumanoidBone.leftFoot: LEG_COORDS,
    HumanoidBone.rightUpperLeg: LEG_COORDS,
    HumanoidBone.rightLowerLeg: LEG_COORDS,
    HumanoidBone.rightFoot: LEG_COORDS,
    HumanoidBone.leftToes: TOES_COORDS,
    HumanoidBone.rightToes: TOES_COORDS,
    HumanoidBone.leftThumbProximal: LEFT_THUMB_COORDS,
    HumanoidBone.leftThumbIntermediate: LEFT_THUMB_COORDS,
    HumanoidBone.leftThumbDistal: LEFT_THUMB_COORDS,
    HumanoidBone.leftIndexProximal: LEFT_HAND_COORDS,
    HumanoidBone.leftIndexIntermediate: LEFT_HAND_COORDS,
    HumanoidBone.leftIndexDistal: LEFT_HAND_COORDS,
    HumanoidBone.leftMiddleProximal: LEFT_HAND_COORDS,
    HumanoidBone.leftMiddleIntermediate: LEFT_HAND_COORDS,
    HumanoidBone.leftMiddleDistal: LEFT_HAND_COORDS,
    HumanoidBone.leftRingProximal: LEFT_HAND_COORDS,
    HumanoidBone.leftRingIntermediate: LEFT_HAND_COORDS,
    HumanoidBone.leftRingDistal: LEFT_HAND_COORDS,
    HumanoidBone.leftLittleProximal: LEFT_HAND_COORDS,
    HumanoidBone.leftLittleIntermediate: LEFT_HAND_COORDS,
    HumanoidBone.leftLittleDistal: LEFT_HAND_COORDS,
    HumanoidBone.rightThumbProximal: RIGHT_THUMB_COORDS,
    HumanoidBone.rightThumbIntermediate: RIGHT_THUMB_COORDS,
    HumanoidBone.rightThumbDistal: RIGHT_THUMB_COORDS,
    HumanoidBone.rightIndexProximal: RIGHT_HAND_COORDS,
    HumanoidBone.rightIndexIntermediate: RIGHT_HAND_COORDS,
    HumanoidBone.rightIndexDistal: RIGHT_HAND_COORDS,
    HumanoidBone.rightMiddleProximal: RIGHT_HAND_COORDS,
    HumanoidBone.rightMiddleIntermediate: RIGHT_HAND_COORDS,
    HumanoidBone.rightMiddleDistal: RIGHT_HAND_COORDS,
    HumanoidBone.rightRingProximal: RIGHT_HAND_COORDS,
    HumanoidBone.rightRingIntermediate: RIGHT_HAND_COORDS,
    HumanoidBone.rightRingDistal: RIGHT_HAND_COORDS,
    HumanoidBone.rightLittleProximal: RIGHT_HAND_COORDS,
    HumanoidBone.rightLittleIntermediate: RIGHT_HAND_COORDS,
    HumanoidBone.rightLittleDistal: RIGHT_HAND_COORDS,
}
