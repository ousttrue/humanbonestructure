from enum import Enum


class HumanoidBone(Enum):
    hips = "hips"
    spine = "spine"
    chest = "chest"
    upperChest = "upperChest"
    neck = "neck"
    head = "head"
    leftEye = "leftEye"
    rightEye = "rightEye"
    jaw = "jaw"
    leftUpperLeg = "leftUpperLeg"
    leftLowerLeg = "leftLowerLeg"
    leftFoot = "leftFoot"
    leftToes = "leftToes"
    rightUpperLeg = "rightUpperLeg"
    rightLowerLeg = "rightLowerLeg"
    rightFoot = "rightFoot"
    rightToes = "rightToes"
    leftShoulder = "leftShoulder"
    leftUpperArm = "leftUpperArm"
    leftLowerArm = "leftLowerArm"
    leftHand = "leftHand"
    rightShoulder = "rightShoulder"
    rightUpperArm = "rightUpperArm"
    rightLowerArm = "rightLowerArm"
    rightHand = "rightHand"
    leftThumbProximal = "leftThumbProximal"
    leftThumbIntermediate = "leftThumbIntermediate"
    leftThumbDistal = "leftThumbDistal"
    leftIndexProximal = "leftIndexProximal"
    leftIndexIntermediate = "leftIndexIntermediate"
    leftIndexDistal = "leftIndexDistal"
    leftMiddleProximal = "leftMiddleProximal"
    leftMiddleIntermediate = "leftMiddleIntermediate"
    leftMiddleDistal = "leftMiddleDistal"
    leftRingProximal = "leftRingProximal"
    leftRingIntermediate = "leftRingIntermediate"
    leftRingDistal = "leftRingDistal"
    leftLittleProximal = "leftLittleProximal"
    leftLittleIntermediate = "leftLittleIntermediate"
    leftLittleDistal = "leftLittleDistal"
    rightThumbProximal = "rightThumbProximal"
    rightThumbIntermediate = "rightThumbIntermediate"
    rightThumbDistal = "rightThumbDistal"
    rightIndexProximal = "rightIndexProximal"
    rightIndexIntermediate = "rightIndexIntermediate"
    rightIndexDistal = "rightIndexDistal"
    rightMiddleProximal = "rightMiddleProximal"
    rightMiddleIntermediate = "rightMiddleIntermediate"
    rightMiddleDistal = "rightMiddleDistal"
    rightRingProximal = "rightRingProximal"
    rightRingIntermediate = "rightRingIntermediate"
    rightRingDistal = "rightRingDistal"
    rightLittleProximal = "rightLittleProximal"
    rightLittleIntermediate = "rightLittleIntermediate"
    rightLittleDistal = "rightLittleDistal"

    def is_finger(self):
        return self in (
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
        )
