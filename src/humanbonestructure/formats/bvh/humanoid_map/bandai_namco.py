#
#  https://github.com/BandaiNamcoResearchInc/Bandai-Namco-Research-Motiondataset
#
from typing import Dict
from ...humanoid_bones import HumanoidBone

MAP: Dict[str, HumanoidBone] = {
    'Hips': HumanoidBone.hips,
    'Spine': HumanoidBone.spine,
    'Chest': HumanoidBone.chest,
    'Neck': HumanoidBone.neck,
    'Head': HumanoidBone.head,
    'Shoulder_L': HumanoidBone.leftShoulder,
    'UpperArm_L': HumanoidBone.leftUpperArm,
    'LowerArm_L': HumanoidBone.leftLowerArm,
    'Hand_L': HumanoidBone.leftHand,
    'Shoulder_R': HumanoidBone.rightShoulder,
    'UpperArm_R': HumanoidBone.rightUpperArm,
    'LowerArm_R': HumanoidBone.rightLowerArm,
    'Hand_R': HumanoidBone.rightHand,
    'UpperLeg_L': HumanoidBone.leftUpperLeg,
    'LowerLeg_L': HumanoidBone.leftLowerLeg,
    'Foot_L': HumanoidBone.leftFoot,
    'Toes_L': HumanoidBone.leftToes,
    'UpperLeg_R': HumanoidBone.rightUpperLeg,
    'LowerLeg_R': HumanoidBone.rightLowerLeg,
    'Foot_R': HumanoidBone.rightFoot,
    'Toes_R': HumanoidBone.rightToes,
}
