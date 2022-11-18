#
# https://github.com/vrm-c/UniVRM/blob/master/Assets/UniGLTF/Runtime/Resources/test_motion.txt
#
from typing import Dict
from humanbonestructure.humanoid.humanoid_bones import HumanoidBone

MAP: Dict[str, HumanoidBone] = {
    'Hips': HumanoidBone.hips,
    'Spine': HumanoidBone.spine,
    'Spine1': HumanoidBone.chest,
    'Neck': HumanoidBone.neck,
    'Head': HumanoidBone.head,
    'LeftShoulder': HumanoidBone.leftShoulder,
    'LeftArm': HumanoidBone.leftUpperArm,
    'LeftForeArm': HumanoidBone.leftLowerArm,
    'LeftHand': HumanoidBone.leftHand,
    'RightShoulder': HumanoidBone.rightShoulder,
    'RightArm': HumanoidBone.rightUpperArm,
    'RightForeArm': HumanoidBone.rightLowerArm,
    'RightHand': HumanoidBone.rightHand,
    'LeftUpLeg': HumanoidBone.leftUpperLeg,
    'LeftLeg': HumanoidBone.leftLowerLeg,
    'LeftFoot': HumanoidBone.leftFoot,
    'LeftToeBase': HumanoidBone.leftToes,
    'RightUpLeg': HumanoidBone.rightUpperLeg,
    'RightLeg': HumanoidBone.rightLowerLeg,
    'RightFoot': HumanoidBone.rightFoot,
    'RightToeBase': HumanoidBone.rightToes,
}
