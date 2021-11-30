from enum import Enum, auto
from typing import NamedTuple, List
from dataclasses import dataclass


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


class Float3(NamedTuple):
    x: float
    y: float
    z: float


NEXT_ID = 1


@dataclass
class Bone:
    bone: HumanBones
    offset: Float3
    children: List['Bone']
    unique_id: int = -1

    def __post_init__(self):
        global NEXT_ID
        self.unique_id = NEXT_ID
        NEXT_ID += 1

    def __hash__(self) -> int:
        return hash((self.bone, self.offset))

    def traverse(self):
        yield self
        for child in self.children:
            for x in child.traverse():
                yield x


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
    return Bone(HumanBones.Hips, Float3(0, hips_pos, 0), [
        Bone(HumanBones.Spine, Float3(0, hips_len, 0), [
                Bone(HumanBones.Chest, Float3(0, spine_len, 0), [
                    Bone(HumanBones.Neck, Float3(0, chest_len, 0), [
                        Bone(HumanBones.Head, Float3(0, neck_len, 0), [
                            Bone(HumanBones.EndSite, Float3(0, head_len, 0), [])
                        ])
                    ]),
                    Bone(HumanBones.LeftShoulder, Float3(-0.05, 0, 0), [
                        Bone(HumanBones.LeftUpperArm, Float3(-shoulder_len, 0, 0), [
                            Bone(HumanBones.LeftLowerArm, Float3(-upper_arm_len, 0, 0), [
                                Bone(HumanBones.LeftHand, Float3(-lower_arm_len, 0, 0), [
                                    Bone(HumanBones.EndSite,
                                         Float3(-hand_len, 0, 0), [])
                                ])
                            ])
                        ])
                    ]),
                    Bone(HumanBones.RightShoulder, Float3(0.05, 0, 0), [
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
