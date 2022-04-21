from enum import Enum, auto
from typing import NamedTuple, List
from dataclasses import dataclass
from glglue.ctypesmath import Float3, Mat4
from ..formats.humanoid_bones import HumanoidBone


class Bone:
    def __init__(self, bone: HumanoidBone, offset: Float3, children: List['Bone']):
        self.bone = bone
        self.offset = offset
        # children[0] is tail
        self.children = children
        self.world_matrix = Mat4.new_identity()
        self.local_init_matrix = Mat4.new_identity()
        # -1 ~ +1
        self.local_euler = Float3(0, 0, 0)

    def __hash__(self) -> int:
        return hash((self.bone, self.offset))

    def traverse(self):
        yield self
        for child in self.children:
            for x in child.traverse():
                yield x

    def calc_matrix(self, parent_world: Mat4):
        parent_offset = Float3(
            parent_world._41, parent_world._42, parent_world._43)
        t = self.offset + parent_offset

        if self.children:
            y = self.children[0].offset.normalized()
            match self.bone:
                case HumanoidBone.leftToes | HumanoidBone.rightToes:
                    z = Float3(0, 1, 0)
                case _:
                    z = Float3(0, 0, 1)
            x = Float3.cross(y, z)
            z = Float3.cross(x, y)
            world_matrix = Mat4.new_coords(x, y, z, t)
            self.world_matrix = world_matrix
            self.local_init_matrix = self.world_matrix * parent_world.inverse_rigidbody()

        for i, child in enumerate(self.children):
            child.calc_matrix(self.world_matrix)

    def local_euler_matrix(self) -> 'Mat4':
        '''
        ZXY ?
        '''
        x = Mat4.new_axis_angle(Float3(
            self.local_init_matrix._11, self.local_init_matrix._12, self.local_init_matrix._13), self.local_euler.x)
        y = Mat4.new_axis_angle(Float3(
            self.local_init_matrix._21, self.local_init_matrix._22, self.local_init_matrix._23), self.local_euler.y)
        z = Mat4.new_axis_angle(Float3(
            self.local_init_matrix._31, self.local_init_matrix._32, self.local_init_matrix._33), self.local_euler.z)
        # m = y * x * z
        m = y * z * x

        return m


def make_humanoid(hips_pos: float) -> Bone:
    head_len = hips_pos / 5
    neck_len = hips_pos / 5
    chest_len = hips_pos / 5
    spine_len = hips_pos / 5
    hips_len = hips_pos / 5

    shoulder_len = 0.05
    upper_arm_len = 0.3
    lower_arm_len = 0.3
    hand_len = 0.1

    upper_leg_len = hips_pos * 0.5
    lower_leg_len = hips_pos * 0.4
    foot_len = hips_pos * 0.1
    toes_len = hips_pos * 0.05
    root = Bone(HumanoidBone.hips, Float3(0, hips_pos, 0), [
        Bone(HumanoidBone.spine, Float3(0, hips_len, 0), [
            Bone(HumanoidBone.chest, Float3(0, spine_len, 0), [
                Bone(HumanoidBone.neck, Float3(0, chest_len, 0), [
                    Bone(HumanoidBone.head, Float3(0, neck_len, 0), [
                        Bone(HumanoidBone.endSite, Float3(0, head_len, 0), [])
                    ])
                ]),
                Bone(HumanoidBone.leftShoulder, Float3(-0.05, chest_len, 0), [
                    Bone(HumanoidBone.leftUpperArm, Float3(-shoulder_len, 0, 0), [
                        Bone(HumanoidBone.leftLowerArm, Float3(-upper_arm_len, 0, 0), [
                            Bone(HumanoidBone.leftHand, Float3(-lower_arm_len, 0, 0), [
                                Bone(HumanoidBone.endSite,
                                     Float3(-hand_len, 0, 0), [])
                            ])
                        ])
                    ])
                ]),
                Bone(HumanoidBone.rightShoulder, Float3(0.05, chest_len, 0), [
                    Bone(HumanoidBone.rightUpperArm, Float3(shoulder_len, 0, 0), [
                        Bone(HumanoidBone.rightLowerArm, Float3(upper_arm_len, 0, 0), [
                            Bone(HumanoidBone.rightHand, Float3(lower_arm_len, 0, 0), [
                                Bone(HumanoidBone.endSite,
                                     Float3(hand_len, 0, 0), [])
                            ])
                        ])
                    ])
                ])
            ])
        ]),
        Bone(HumanoidBone.leftUpperLeg, Float3(-0.1, 0, 0), [
            Bone(HumanoidBone.leftLowerLeg, Float3(0, -upper_leg_len, 0), [
                Bone(HumanoidBone.leftFoot, Float3(0, -lower_leg_len, 0), [
                    Bone(HumanoidBone.leftToes, Float3(0, -foot_len, 0.1), [
                        Bone(HumanoidBone.endSite, Float3(0, 0, toes_len), [])
                    ])
                ])
            ])
        ]),
        Bone(HumanoidBone.rightUpperLeg, Float3(0.1, 0, 0), [
            Bone(HumanoidBone.rightLowerLeg, Float3(0, -upper_leg_len, 0), [
                Bone(HumanoidBone.rightFoot, Float3(0, -lower_leg_len, 0), [
                    Bone(HumanoidBone.rightToes, Float3(0, -foot_len, 0.1), [
                        Bone(HumanoidBone.endSite, Float3(0, 0, toes_len), [])
                    ])
                ])
            ])]),
    ])

    root.calc_matrix(Mat4.new_identity())

    return root
