from enum import Enum, auto
from typing import NamedTuple, List
from dataclasses import dataclass
from glglue.ctypesmath import Float3, Mat4


class HumanBones(Enum):
    EndSite = auto()
    Hips = auto()
    Spine = auto()
    Chest = auto()
    Neck = auto()
    Head = auto()

    LeftShoulder = auto()
    LeftUpperArm = auto()
    LeftLowerArm = auto()
    LeftHand = auto()

    RightShoulder = auto()
    RightUpperArm = auto()
    RightLowerArm = auto()
    RightHand = auto()

    LeftUpperLeg = auto()
    LeftLowerLeg = auto()
    LeftFoot = auto()
    LeftToes = auto()

    RightUpperLeg = auto()
    RightLowerLeg = auto()
    RightFoot = auto()
    RightToes = auto()


class Bone:
    def __init__(self, bone: HumanBones, offset: Float3, children: List['Bone']):
        self.bone = bone
        self.offset = offset
        # children[0] is tail
        self.children = children
        self.world_matrix = Mat4.new_identity()
        self.local_init_matrix = Mat4.new_identity()
        # -1 ~ +1
        self.local_rotation_main = 0
        self.local_rotation_sub = 0
        self.local_rotation_roll = 0

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
                case HumanBones.LeftToes | HumanBones.RightToes:
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
        main = Mat4.new_axis_angle(Float3(
            self.local_init_matrix._11, self.local_init_matrix._12, self.local_init_matrix._13), self.local_rotation_main)
        sub = Mat4.new_axis_angle(Float3(
            self.local_init_matrix._21, self.local_init_matrix._22, self.local_init_matrix._23), self.local_rotation_sub)
        roll = Mat4.new_axis_angle(Float3(
            self.local_init_matrix._31, self.local_init_matrix._32, self.local_init_matrix._33), self.local_rotation_roll)
        m = roll * sub * main

        if m != Mat4.new_identity():
            pass

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
    root = Bone(HumanBones.Hips, Float3(0, hips_pos, 0), [
        Bone(HumanBones.Spine, Float3(0, hips_len, 0), [
            Bone(HumanBones.Chest, Float3(0, spine_len, 0), [
                Bone(HumanBones.Neck, Float3(0, chest_len, 0), [
                    Bone(HumanBones.Head, Float3(0, neck_len, 0), [
                        Bone(HumanBones.EndSite, Float3(0, head_len, 0), [])
                    ])
                ]),
                Bone(HumanBones.LeftShoulder, Float3(-0.05, chest_len, 0), [
                    Bone(HumanBones.LeftUpperArm, Float3(-shoulder_len, 0, 0), [
                        Bone(HumanBones.LeftLowerArm, Float3(-upper_arm_len, 0, 0), [
                            Bone(HumanBones.LeftHand, Float3(-lower_arm_len, 0, 0), [
                                Bone(HumanBones.EndSite,
                                     Float3(-hand_len, 0, 0), [])
                            ])
                        ])
                    ])
                ]),
                Bone(HumanBones.RightShoulder, Float3(0.05, chest_len, 0), [
                    Bone(HumanBones.RightUpperArm, Float3(shoulder_len, 0, 0), [
                        Bone(HumanBones.RightLowerArm, Float3(upper_arm_len, 0, 0), [
                            Bone(HumanBones.RightHand, Float3(lower_arm_len, 0, 0), [
                                Bone(HumanBones.EndSite,
                                     Float3(hand_len, 0, 0), [])
                            ])
                        ])
                    ])
                ])
            ])
        ]),
        Bone(HumanBones.LeftUpperLeg, Float3(-0.1, 0, 0), [
            Bone(HumanBones.LeftLowerLeg, Float3(0, -upper_leg_len, 0), [
                Bone(HumanBones.LeftFoot, Float3(0, -lower_leg_len, 0), [
                    Bone(HumanBones.LeftToes, Float3(0, -foot_len, 0.1), [
                        Bone(HumanBones.EndSite, Float3(0, 0, toes_len), [])
                    ])
                ])
            ])
        ]),
        Bone(HumanBones.RightUpperLeg, Float3(0.1, 0, 0), [
            Bone(HumanBones.RightLowerLeg, Float3(0, -upper_leg_len, 0), [
                Bone(HumanBones.RightFoot, Float3(0, -lower_leg_len, 0), [
                    Bone(HumanBones.RightToes, Float3(0, -foot_len, 0.1), [
                        Bone(HumanBones.EndSite, Float3(0, 0, toes_len), [])
                    ])
                ])
            ])]),
    ])

    root.calc_matrix(Mat4.new_identity())

    return root
