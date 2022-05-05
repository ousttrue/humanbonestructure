#
# http://drf.co.jp/liveanimation/
#
from typing import Dict
from ...humanoid_bones import HumanoidBone

MAP: Dict[str, HumanoidBone] = {
    'Hips': HumanoidBone.hips,
    'Chest': HumanoidBone.spine,
    'Chest2': HumanoidBone.chest,
    'Neck': HumanoidBone.neck,
    'Head': HumanoidBone.head,
    'LeftCollar': HumanoidBone.leftShoulder,
    'LeftShoulder': HumanoidBone.leftUpperArm,
    'LeftElbow': HumanoidBone.leftLowerArm,
    'LeftWrist': HumanoidBone.leftHand,
    'RightCollar': HumanoidBone.rightShoulder,
    'RightShoulder': HumanoidBone.rightUpperArm,
    'RightElbow': HumanoidBone.rightLowerArm,
    'RightWrist': HumanoidBone.rightHand,
    'LeftHip': HumanoidBone.leftUpperLeg,
    'LeftKnee': HumanoidBone.leftLowerLeg,
    'LeftAnkle': HumanoidBone.leftFoot,
    'RightHip': HumanoidBone.rightUpperLeg,
    'RightKnee': HumanoidBone.rightLowerLeg,
    'RightAnkle': HumanoidBone.rightFoot,
}
