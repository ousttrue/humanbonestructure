from typing import Set
import math
import glm
from ..humanoid.pose import Motion, Pose, BonePose
from .humanoid_bones import HumanoidBone
from ..humanoid.transform import Transform


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

            #
            BonePose('rightHand', HumanoidBone.rightHand,
                     Transform.identity()),
            # thumb: 1, 2, 3, 4
            BonePose('rightThumbProximal',
                     HumanoidBone.rightThumbProximal, Transform.identity()),
            BonePose('rightThumbIntermediate',
                     HumanoidBone.rightThumbIntermediate, Transform.identity()),
            BonePose('rightThumbDistal', HumanoidBone.rightThumbDistal,
                     Transform.identity()),
            BonePose('rightThumbTip', HumanoidBone.rightThumbTip,
                     Transform.identity()),
            # index: 5, 6, 7, 8
            BonePose('rightIndexProximal',
                     HumanoidBone.rightIndexProximal, Transform.identity()),
            BonePose('rightIndexIntermediate',
                     HumanoidBone.rightIndexIntermediate, Transform.identity()),
            BonePose('rightIndexDistal', HumanoidBone.rightIndexDistal,
                     Transform.identity()),
            BonePose('rightIndexTip', HumanoidBone.rightIndexTip,
                     Transform.identity()),
            # middle: 9, 10, 11, 12
            BonePose('rightMiddleProximal',
                     HumanoidBone.rightMiddleProximal, Transform.identity()),
            BonePose('rightMiddleIntermediate',
                     HumanoidBone.rightMiddleIntermediate, Transform.identity()),
            BonePose('rightMiddleDistal', HumanoidBone.rightMiddleDistal,
                     Transform.identity()),
            BonePose('rightMiddleTip', HumanoidBone.rightMiddleTip,
                     Transform.identity()),
            # ring: 13, 14, 15, 16
            BonePose('rightRingProximal', HumanoidBone.rightRingProximal,
                     Transform.identity()),
            BonePose('rightRingIntermediate',
                     HumanoidBone.rightRingIntermediate, Transform.identity()),
            BonePose('rightRingDistal', HumanoidBone.rightRingDistal,
                     Transform.identity()),
            BonePose('rightRingTip', HumanoidBone.rightRingTip,
                     Transform.identity()),
            # little: 17, 18, 19, 20
            BonePose('rightLittleProximal',
                     HumanoidBone.rightLittleProximal, Transform.identity()),
            BonePose('rightLittleIntermediate',
                     HumanoidBone.rightLittleIntermediate, Transform.identity()),
            BonePose('rightLittleDistal', HumanoidBone.rightLittleDistal,
                     Transform.identity()),
            BonePose('rightLittleTip', HumanoidBone.rightLittleTip,
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

            self.make_handpose(left, 0, glm.vec3(0, 0, -1))
            self.make_handpose(right, 21, glm.vec3(0, 0, 1))

    def make_handpose(self, landmarks, offset: int, axis: glm.vec3):
        if not landmarks:
            return
        points = {
            i: glm.vec3(v.x, -v.y, -v.z) for i, v in enumerate(landmarks)
        }
        # thumb
        t_axis = glm.normalize(glm.vec3(-1, 1, 0))
        _01 = glm.normalize(points[1] - points[0])
        _a = glm.normalize(points[2] - points[1])
        _b = glm.normalize(points[3]-points[2])
        _c = glm.normalize(points[4]-points[3])
        _a_angle = math.acos(glm.dot(_01, _a))
        _b_angle = math.acos(glm.dot(_a, _b))
        _c_angle = math.acos(glm.dot(_b, _c))
        bone_a = self._pose.bones[offset+1]
        self._pose.bones[offset+1] = BonePose(
            bone_a.name, bone_a.humanoid_bone, bone_a.transform._replace(rotation=glm.angleAxis(_a_angle, t_axis)))
        bone_b = self._pose.bones[offset+2]
        self._pose.bones[offset+2] = BonePose(
            bone_b.name, bone_b.humanoid_bone, bone_b.transform._replace(rotation=glm.angleAxis(_b_angle, t_axis)))
        bone_c = self._pose.bones[offset+3]
        self._pose.bones[offset+3] = BonePose(
            bone_c.name, bone_c.humanoid_bone, bone_c.transform._replace(rotation=glm.angleAxis(_c_angle, t_axis)))

        # index, middle, ring, little
        _09 = glm.normalize(points[9]-points[0])
        self.make_fingerpose(points, offset, axis, _09, 5, 6, 7, 8)
        self.make_fingerpose(points, offset, axis, _09, 9, 10, 11, 12)
        self.make_fingerpose(points, offset, axis, _09, 13, 14, 15, 16)
        self.make_fingerpose(points, offset, axis, _09, 17, 18, 19, 20)

    def make_fingerpose(self, points, offset: int, axis: glm.vec3, _0, i0, i1, i2, i3):
        _a = glm.normalize(points[i3] - points[i2])
        _b = glm.normalize(points[i2]-points[i1])
        _c = glm.normalize(points[i1]-points[i0])
        _a_angle = math.acos(glm.dot(_0, _a))
        _b_angle = math.acos(glm.dot(_a, _b))
        _c_angle = math.acos(glm.dot(_b, _c))
        bone_a = self._pose.bones[offset+i0]
        self._pose.bones[offset+i0] = BonePose(
            bone_a.name, bone_a.humanoid_bone, bone_a.transform._replace(rotation=glm.angleAxis(_a_angle, axis)))
        bone_b = self._pose.bones[offset+i1]
        self._pose.bones[offset+i1] = BonePose(
            bone_b.name, bone_b.humanoid_bone, bone_b.transform._replace(rotation=glm.angleAxis(_b_angle, axis)))
        bone_c = self._pose.bones[offset+i2]
        self._pose.bones[offset+i2] = BonePose(
            bone_c.name, bone_c.humanoid_bone, bone_c.transform._replace(rotation=glm.angleAxis(_c_angle, axis)))
