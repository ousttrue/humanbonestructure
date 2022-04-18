from typing import Set
from .pose import Motion, Pose
from .humanoid_bones import HumanoidBone


class HandPose(Motion):
    def __init__(self) -> None:
        super().__init__('mediapipe Handpose')
        self._humanoid_bones = set([
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
        self._pose = Pose(self.name)

    def get_humanbones(self) -> Set[HumanoidBone]:
        return self._humanoid_bones

    def get_current_pose(self) -> Pose:
        return self._pose
