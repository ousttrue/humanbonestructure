from typing import Set
import glm
from .pose import Motion, Pose, BonePose
from .humanoid_bones import HumanoidBone
from .transform import Transform


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

        # 21 bones in media pipe
        self._pose.bones = [
            BonePose('leftHand', HumanoidBone.leftHand, Transform.identity()),
            # thumb: 1, 2, 3, 4
            BonePose('leftThumbProximal',
                     HumanoidBone.leftThumbProximal, Transform.identity()),
            BonePose('leftThumbIntermediate',
                     HumanoidBone.leftThumbIntermediate, Transform.identity()),
            BonePose('leftThumbDistal', HumanoidBone.leftThumbDistal,
                     Transform.identity()),
            BonePose('leftThumbTip', HumanoidBone.leftThumbTip,
                     Transform.identity()),
            # index: 5, 6, 7, 8
            BonePose('leftIndexProximal',
                     HumanoidBone.leftIndexProximal, Transform.identity()),
            BonePose('leftIndexIntermediate',
                     HumanoidBone.leftIndexIntermediate, Transform.identity()),
            BonePose('leftIndexDistal', HumanoidBone.leftIndexDistal,
                     Transform.identity()),
            BonePose('leftIndexTip', HumanoidBone.leftIndexTip,
                     Transform.identity()),
            # middle: 9, 10, 11, 12
            BonePose('leftMiddleProximal',
                     HumanoidBone.leftMiddleProximal, Transform.identity()),
            BonePose('leftMiddleIntermediate',
                     HumanoidBone.leftMiddleIntermediate, Transform.identity()),
            BonePose('leftMiddleDistal', HumanoidBone.leftMiddleDistal,
                     Transform.identity()),
            BonePose('leftMiddleTip', HumanoidBone.leftMiddleTip,
                     Transform.identity()),
            # ring: 13, 14, 15, 16
            BonePose('leftRingProximal', HumanoidBone.leftRingProximal,
                     Transform.identity()),
            BonePose('leftRingIntermediate',
                     HumanoidBone.leftRingIntermediate, Transform.identity()),
            BonePose('leftRingDistal', HumanoidBone.leftRingDistal,
                     Transform.identity()),
            BonePose('leftRingTip', HumanoidBone.leftRingTip,
                     Transform.identity()),
            # little: 17, 18, 19, 20
            BonePose('leftLittleProximal',
                     HumanoidBone.leftLittleProximal, Transform.identity()),
            BonePose('leftLittleIntermediate',
                     HumanoidBone.leftLittleIntermediate, Transform.identity()),
            BonePose('leftLittleDistal', HumanoidBone.leftLittleDistal,
                     Transform.identity()),
            BonePose('leftLittleTip', HumanoidBone.leftLittleTip,
                     Transform.identity()),
        ]

    def get_humanbones(self) -> Set[HumanoidBone]:
        return self._humanoid_bones

    def get_current_pose(self) -> Pose:
        return self._pose

    def update(self, results):
        # update vertices

        if results.multi_hand_world_landmarks:
            left = None
            right = None
            for hand_landmarks, handedness in zip(results.multi_hand_world_landmarks, results.multi_handedness):
                hand_class = handedness.classification[0]

                # label の left が右手
                # 入力画像の上下反転とかの影響かも
                if hand_class.label == 'Left':
                    right = hand_landmarks.landmark
                elif hand_class.label == 'Right':
                    left = hand_landmarks.landmark

                break

    def make_handpose(self, left_landmarks, right_landmarks):
        points_l = {
            i: glm.vec3(v.x, -v.y, -v.z) for i, v in enumerate(left_landmarks)
        }
        _56 = glm.normalize(points_l[6] - points_l[5])
        _67 = glm.normalize(points_l[7]-points_l[6])
        _6_angle = glm.dot(_56, _67)
        _6 = self._pose.bones[6]
        self._pose.bones[6] = BonePose(
            _6.name, _6.humanoid_bone, _6.transform._replace(rotation=glm.angleAxis(_6_angle, glm.vec3(0, 0, 1))))
