import glm
from ..humanoid.humanoid_bones import HumanoidBone
from .bone_shape import Coordinate, BLENDER_COORDS


UNITYCHAN_COORDS_LEG = Coordinate(
    yaw=glm.vec3(0, -1, 0),
    pitch=glm.vec3(0, 0, -1),
    roll=glm.vec3(1, 0, 0))

UNITYCHAN_COORDS = Coordinate(
    yaw=glm.vec3(0, 1, 0),
    pitch=glm.vec3(0, 0, 1),
    roll=glm.vec3(1, 0, 0))

UNITYCHAN_COORDS_ARM = Coordinate(
    yaw=glm.vec3(0, 1, 0),
    pitch=glm.vec3(0, 0, 1),
    roll=glm.vec3(1, 0, 0))


UNITYCHAN_COORDS_HAND = Coordinate(
    yaw=glm.vec3(0, 0, 1),
    pitch=glm.vec3(0, -1, 0),
    roll=glm.vec3(1, 0, 0))

UNITYCHAN_COORDS_HAND_R = Coordinate(
    yaw=glm.vec3(0, 0, -1),
    pitch=glm.vec3(0, 1, 0),
    roll=glm.vec3(1, 0, 0))


UNITYCHAN_COORDS_MAP = {
    HumanoidBone.head: UNITYCHAN_COORDS,
    HumanoidBone.neck: UNITYCHAN_COORDS,
    HumanoidBone.chest: UNITYCHAN_COORDS,
    HumanoidBone.spine: UNITYCHAN_COORDS,
    HumanoidBone.hips: UNITYCHAN_COORDS,
    # left
    HumanoidBone.leftShoulder: UNITYCHAN_COORDS_ARM,
    HumanoidBone.leftUpperArm: UNITYCHAN_COORDS_ARM,
    HumanoidBone.leftLowerArm: UNITYCHAN_COORDS_ARM,
    HumanoidBone.leftHand: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftThumbProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftThumbIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftThumbDistal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftIndexProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftIndexIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftIndexDistal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftMiddleProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftMiddleIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftMiddleDistal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftRingProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftRingIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftRingDistal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftLittleProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftLittleIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.leftLittleDistal: UNITYCHAN_COORDS_HAND,
    # right
    HumanoidBone.rightShoulder: UNITYCHAN_COORDS_ARM,
    HumanoidBone.rightUpperArm: UNITYCHAN_COORDS_ARM,
    HumanoidBone.rightLowerArm: UNITYCHAN_COORDS_ARM,
    HumanoidBone.rightHand: UNITYCHAN_COORDS_HAND_R,
    HumanoidBone.rightThumbProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightThumbIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightThumbDistal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightIndexProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightIndexIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightIndexDistal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightMiddleProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightMiddleIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightMiddleDistal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightRingProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightRingIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightRingDistal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightLittleProximal: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightLittleIntermediate: UNITYCHAN_COORDS_HAND,
    HumanoidBone.rightLittleDistal: UNITYCHAN_COORDS_HAND,
    # leg
    HumanoidBone.leftUpperLeg: UNITYCHAN_COORDS_LEG,
    HumanoidBone.leftLowerLeg: UNITYCHAN_COORDS_LEG,
    HumanoidBone.leftFoot: UNITYCHAN_COORDS_LEG,
    HumanoidBone.leftToes: UNITYCHAN_COORDS_LEG,
    HumanoidBone.rightUpperLeg: UNITYCHAN_COORDS_LEG,
    HumanoidBone.rightLowerLeg: UNITYCHAN_COORDS_LEG,
    HumanoidBone.rightFoot: UNITYCHAN_COORDS_LEG,
    HumanoidBone.rightToes: UNITYCHAN_COORDS_LEG,
}


def get_unitychan_coords(humanoid_bone: HumanoidBone) -> Coordinate:
    return UNITYCHAN_COORDS_MAP.get(humanoid_bone, BLENDER_COORDS)
