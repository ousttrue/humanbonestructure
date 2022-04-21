from typing import List
import glm
from ..formats.humanoid_bones import HumanoidBone


class Bone:
    def __init__(self, bone: HumanoidBone, offset: glm.vec3, children: List['Bone']):
        self.bone = bone
        self.offset = offset
        # children[0] is tail
        self.children = children
        self.world_matrix = glm.mat4()
        self.local_init_matrix = glm.mat4()
        # -1 ~ +1
        self.local_euler = glm.vec3(0)

    def __hash__(self) -> int:
        return hash((self.bone, self.offset))

    def traverse(self):
        yield self
        for child in self.children:
            for x in child.traverse():
                yield x

    def calc_matrix(self, parent_world: glm.mat4):
        parent_offset = parent_world[3].xyz
        t = self.offset + parent_offset

        if self.children:
            y = glm.normalize(self.children[0].offset)
            match self.bone:
                case HumanoidBone.leftToes | HumanoidBone.rightToes:
                    z = glm.vec3(0, 1, 0)
                case _:
                    z = glm.vec3(0, 0, 1)
            x = glm.cross(y, z)
            z = glm.cross(x, y)
            world_matrix = glm.mat4(
                glm.vec4(x, 0),
                glm.vec4(y, 0),
                glm.vec4(z, 0),
                glm.vec4(t, 1))
            self.world_matrix = world_matrix
            self.local_init_matrix = glm.inverse(parent_world) * self.world_matrix

        for i, child in enumerate(self.children):
            child.calc_matrix(self.world_matrix)

    def local_euler_matrix(self) -> glm.mat4:
        '''
        ZXY ?
        '''
        x = glm.angleAxis(self.local_euler.x, self.local_init_matrix[0].xyz)
        y = glm.angleAxis(self.local_euler.y, self.local_init_matrix[1].xyz)
        z = glm.angleAxis(self.local_euler.z, self.local_init_matrix[2].xyz)
        # m = y * x * z
        # m = y * z * x
        m = x * z * y
        return glm.mat4(m)


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
    root = Bone(HumanoidBone.hips, glm.vec3(0, hips_pos, 0), [
        Bone(HumanoidBone.spine, glm.vec3(0, hips_len, 0), [
            Bone(HumanoidBone.chest, glm.vec3(0, spine_len, 0), [
                Bone(HumanoidBone.neck, glm.vec3(0, chest_len, 0), [
                    Bone(HumanoidBone.head, glm.vec3(0, neck_len, 0), [
                        Bone(HumanoidBone.endSite, glm.vec3(0, head_len, 0), [])
                    ])
                ]),
                Bone(HumanoidBone.leftShoulder, glm.vec3(-0.05, chest_len, 0), [
                    Bone(HumanoidBone.leftUpperArm, glm.vec3(-shoulder_len, 0, 0), [
                        Bone(HumanoidBone.leftLowerArm, glm.vec3(-upper_arm_len, 0, 0), [
                            Bone(HumanoidBone.leftHand, glm.vec3(-lower_arm_len, 0, 0), [
                                Bone(HumanoidBone.endSite,
                                     glm.vec3(-hand_len, 0, 0), [])
                            ])
                        ])
                    ])
                ]),
                Bone(HumanoidBone.rightShoulder, glm.vec3(0.05, chest_len, 0), [
                    Bone(HumanoidBone.rightUpperArm, glm.vec3(shoulder_len, 0, 0), [
                        Bone(HumanoidBone.rightLowerArm, glm.vec3(upper_arm_len, 0, 0), [
                            Bone(HumanoidBone.rightHand, glm.vec3(lower_arm_len, 0, 0), [
                                Bone(HumanoidBone.endSite,
                                     glm.vec3(hand_len, 0, 0), [])
                            ])
                        ])
                    ])
                ])
            ])
        ]),
        Bone(HumanoidBone.leftUpperLeg, glm.vec3(-0.1, 0, 0), [
            Bone(HumanoidBone.leftLowerLeg, glm.vec3(0, -upper_leg_len, 0), [
                Bone(HumanoidBone.leftFoot, glm.vec3(0, -lower_leg_len, 0), [
                    Bone(HumanoidBone.leftToes, glm.vec3(0, -foot_len, 0.1), [
                        Bone(HumanoidBone.endSite, glm.vec3(0, 0, toes_len), [])
                    ])
                ])
            ])
        ]),
        Bone(HumanoidBone.rightUpperLeg, glm.vec3(0.1, 0, 0), [
            Bone(HumanoidBone.rightLowerLeg, glm.vec3(0, -upper_leg_len, 0), [
                Bone(HumanoidBone.rightFoot, glm.vec3(0, -lower_leg_len, 0), [
                    Bone(HumanoidBone.rightToes, glm.vec3(0, -foot_len, 0.1), [
                        Bone(HumanoidBone.endSite, glm.vec3(0, 0, toes_len), [])
                    ])
                ])
            ])]),
    ])

    root.calc_matrix(glm.mat4())

    return root
