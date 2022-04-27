from typing import List
import glm
from ..node import Node
from ...formats.humanoid_bones import HumanoidBone
from ...formats.transform import Transform


BODY = [
    HumanoidBone.hips,
    HumanoidBone.spine,
    HumanoidBone.chest,
    HumanoidBone.neck,
    HumanoidBone.head,
    HumanoidBone.endSite,
]

LEFT_LEG = [
    HumanoidBone.leftUpperLeg,
    HumanoidBone.leftLowerLeg,
    HumanoidBone.leftFoot,
    HumanoidBone.leftToes,
    HumanoidBone.endSite,
]

LEFT_ARM = [
    HumanoidBone.leftShoulder,
    HumanoidBone.leftUpperArm,
    HumanoidBone.leftLowerArm,
    HumanoidBone.leftHand,
    HumanoidBone.endSite,
]

LEFT_BONES = [
    HumanoidBone.leftThumbProximal,
    HumanoidBone.leftThumbIntermediate,
    HumanoidBone.leftThumbDistal,
    HumanoidBone.endSite,

    HumanoidBone.leftIndexProximal,
    HumanoidBone.leftIndexIntermediate,
    HumanoidBone.leftIndexDistal,
    HumanoidBone.endSite,

    HumanoidBone.leftMiddleProximal,
    HumanoidBone.leftMiddleIntermediate,
    HumanoidBone.leftMiddleDistal,
    HumanoidBone.endSite,

    HumanoidBone.leftRingProximal,
    HumanoidBone.leftRingIntermediate,
    HumanoidBone.leftRingDistal,
    HumanoidBone.endSite,

    HumanoidBone.leftLittleProximal,
    HumanoidBone.leftLittleIntermediate,
    HumanoidBone.leftLittleDistal,
    HumanoidBone.endSite,
]

RIGHT_ARM = [
    HumanoidBone.rightShoulder,
    HumanoidBone.rightUpperArm,
    HumanoidBone.rightLowerArm,
    HumanoidBone.rightHand,
]

RIGHT_BONES = [
    HumanoidBone.rightThumbProximal,
    HumanoidBone.rightThumbIntermediate,
    HumanoidBone.rightThumbDistal,
    HumanoidBone.endSite,

    HumanoidBone.rightIndexProximal,
    HumanoidBone.rightIndexIntermediate,
    HumanoidBone.rightIndexDistal,
    HumanoidBone.endSite,

    HumanoidBone.rightMiddleProximal,
    HumanoidBone.rightMiddleIntermediate,
    HumanoidBone.rightMiddleDistal,
    HumanoidBone.endSite,

    HumanoidBone.rightRingProximal,
    HumanoidBone.rightRingIntermediate,
    HumanoidBone.rightRingDistal,
    HumanoidBone.endSite,

    HumanoidBone.rightLittleProximal,
    HumanoidBone.rightLittleIntermediate,
    HumanoidBone.rightLittleDistal,
    HumanoidBone.endSite,
]

RIGHT_LEG = [
    HumanoidBone.rightUpperLeg,
    HumanoidBone.rightLowerLeg,
    HumanoidBone.rightFoot,
    HumanoidBone.rightToes,
    HumanoidBone.endSite,
]


def _create_hand(forward: glm.vec3, up: glm.vec3, thumb: glm.vec3, bones: List[HumanoidBone]) -> Node:
    fl = 0.015
    d = 0.015
    return Node(bones[0].name, Transform.from_translation(forward * fl), humanoid_bone=bones[0], children=[
        # thumb
        Node(bones[1].name, Transform.from_translation(-thumb*d-up*fl), humanoid_bone=bones[1], children=[
            Node(bones[2].name, Transform.from_translation(forward*fl*2), humanoid_bone=bones[2], children=[
                Node(bones[3].name, Transform.from_translation(forward*fl), humanoid_bone=bones[3], children=[
                    Node(bones[4].name, Transform.from_translation(forward*fl), humanoid_bone=bones[4], children=[
                    ])
                ])
            ])
        ]),
        # fingers
        Node(i+5, bones[5].name, Transform.from_translation(forward*fl*3.5-thumb*d), humanoid_bone=bones[5], children=[
            Node(i+6, bones[6].name, Transform.from_translation(forward*fl*2), humanoid_bone=bones[6], children=[
                Node(i+7, bones[7].name, Transform.from_translation(forward*fl), humanoid_bone=bones[7], children=[
                    Node(i+8, bones[8].name, Transform.from_translation(forward*fl), humanoid_bone=bones[8], children=[
                    ])
                ])
            ])
        ]),
        Node(i+9, bones[9].name, Transform.from_translation(forward*fl*4), humanoid_bone=bones[9], children=[
            Node(i+10, bones[10].name, Transform.from_translation(forward*fl*2), humanoid_bone=bones[10], children=[
                Node(i+11, bones[11].name, Transform.from_translation(forward*fl), humanoid_bone=bones[11], children=[
                    Node(i+12, bones[12].name, Transform.from_translation(forward*fl), humanoid_bone=bones[12], children=[
                    ])
                ])
            ])
        ]),
        Node(i+13, bones[13].name, Transform.from_translation(forward*fl*3.5+thumb*d), humanoid_bone=bones[13], children=[
            Node(i+14, bones[14].name, Transform.from_translation(forward*fl*2), humanoid_bone=bones[14], children=[
                Node(i+15, bones[15].name, Transform.from_translation(forward*fl), humanoid_bone=bones[15], children=[
                    Node(i+16, bones[16].name, Transform.from_translation(forward*fl), humanoid_bone=bones[16], children=[
                    ])
                ])
            ])
        ]),
        Node(i+17, bones[17].name, Transform.from_translation(forward*fl*3+thumb*d*2), humanoid_bone=bones[17], children=[
            Node(i+18, bones[18].name, Transform.from_translation(forward*fl*2), humanoid_bone=bones[18], children=[
                Node(i+19, bones[19].name, Transform.from_translation(forward*fl), humanoid_bone=bones[19], children=[
                    Node(i+20, bones[20].name, Transform.from_translation(forward*fl), humanoid_bone=bones[20], children=[
                    ])
                ])
            ])
        ]),
    ])


def _create(pos: glm.vec3, dir: glm.vec3, human_bones: List[HumanoidBone], *values) -> Node:
    '''
    shoulder, upperArm, lowerArm, hand
    '''
    root = Node(human_bones[0].name, Transform.from_translation(
        pos), humanoid_bone=human_bones[0])
    parent = root
    for humanoid_bone, value in zip(human_bones[1:], values):
        node = Node(humanoid_bone.name, Transform.from_translation(
            dir * value), humanoid_bone=humanoid_bone)
        parent.add_child(node)
        parent = node

    return root


def _create_body(*values: float) -> Node:
    '''
    hips, spine, chest, neck, head, head_end
    '''
    bones: List[Node] = []
    for humanoid_bone, value in zip(BODY, values):
        node = Node(humanoid_bone.name, Transform.from_translation(
            glm.vec3(0, value, 0)), humanoid_bone=humanoid_bone)
        if bones:
            bones[-1].add_child(node)
        bones.append(node)



    return bones[0]


def create() -> Node:
    '''
    A
    | forward
    ||||
    |||| |
    ロロ/  thumb->
    <-x
    '''
    root = Node('root', Transform.identity())

    body = _create(glm.vec3(0, 0.8, 0), glm.vec3(0, 1, 0), BODY,
                       0.3, 0.3, 0.1, 0.2)

    #
    left_arm = _create(glm.vec3(0.1, 0, 0), glm.vec3(1, 0, 0), LEFT_ARM,
                       0.1, 0.3, 0.3, 0.2)
    body.find_humanoid_bone(HumanoidBone.chest).add_child(left_arm) # type: ignore
    #
    right_arm = _create(glm.vec3(-0.1, 0, 0), glm.vec3(-1, 0, 0), LEFT_ARM,
                        0.1, 0.3, 0.3, 0.2)
    body.find_humanoid_bone(HumanoidBone.chest).add_child(right_arm) # type: ignore
    #
    left_leg = _create(glm.vec3(0.1, 0, 0), glm.vec3(0, -1, 0), LEFT_ARM,
                       0.3, 0.3, 0.2, 0.1)
    body.find_humanoid_bone(HumanoidBone.hips).add_child(left_leg) # type: ignore
    #
    right_leg = _create(glm.vec3(-0.1, 0, 0), glm.vec3(0, -1, 0), LEFT_ARM,
                       0.3, 0.3, 0.2, 0.1)
    body.find_humanoid_bone(HumanoidBone.hips).add_child(right_leg) # type: ignore

    left = _create_hand(0, glm.vec3(1, 0, 0), glm.vec3(
        0, 1, 0), glm.vec3(0, 0, -1), LEFT_BONES)
    right = _create_hand(21, glm.vec3(-1, 0, 0), glm.vec3(
        0, 1, 0), glm.vec3(0, 0, -1), RIGHT_BONES)

    # body = _create_body(0.8, 0.2, 0.2, 0.2, 0.2)
    root.add_child(body)

    return root

    # _create_hand(glm.vec3(0, 1, 0), )

    # root = Node(0, 'root',  Transform.identity(), humanoid_bone=HumanoidBone.leftHand, children=[
    #     Node(1, 'thumb1', Transform.from_translation(glm.vec3(0.1, 0, 0)), humanoid_bone=HumanoidBone.leftThumbProximal, children=[
    #         Node(2, 'thumb2', Transform.from_translation(glm.vec3(0.1, 0, 0)), humanoid_bone=HumanoidBone.leftThumbIntermediate, children=[
    #             Node(3, 'thumb3', Transform.from_translation(glm.vec3(0.1, 0, 0)), humanoid_bone=HumanoidBone.leftThumbDistal, children=[
    #                 Node(4, 'thumb4', Transform.from_translation(glm.vec3(0.1, 0, 0), glm.quat(
    #                 ), glm.vec3(1)), humanoid_bone=HumanoidBone.leftThumbTip)
    #             ])
    #         ])
    #     ]),
    #     Node(5, 'index1', Transform.from_translation(glm.vec3(0.1, 0, -0.1)), humanoid_bone=HumanoidBone.leftIndexProximal, children=[
    #         Node(6, 'index2', Transform.from_translation(glm.vec3(0.1, 0, 0)), humanoid_bone=HumanoidBone.leftIndexIntermediate, children=[
    #             Node(7, 'index3', Transform.from_translation(glm.vec3(0.1, 0, 0)), humanoid_bone=HumanoidBone.leftIndexDistal, children=[
    #                 Node(8, 'index4', Transform.from_translation(glm.vec3(0.1, 0, 0), glm.quat(
    #                 ), glm.vec3(1)), humanoid_bone=HumanoidBone.leftIndexTip)
    #             ])
    #         ])
    #     ]),
    # Node(9, 'middle1', humanoid_bone=HumanoidBone.leftMiddleProximal, Transform.from_translation(glm.vec3(0.1, 0, -0.2), children=[
    #     Node(10, 'middle2', humanoid_bone=HumanoidBone.leftMiddleIntermediate, Transform.from_translation(glm.vec3(0.2, 0, -0.2), children=[
    #         Node(11, 'middle3', humanoid_bone=HumanoidBone.leftMiddleDistal, Transform.from_translation(glm.vec3(0.3, 0, -0.2), children=[
    #             Node(12, 'middle4', Transform.from_translation(glm.vec3(0.4, 0, -0.2))
    #         ])
    #     ])
    # ]),
    # Node(13, 'ring1', humanoid_bone=HumanoidBone.leftRingProximal, Transform.from_translation(glm.vec3(0.1, 0, -0.3), children=[
    #     Node(14, 'ring2', humanoid_bone=HumanoidBone.leftRingIntermediate, Transform.from_translation(glm.vec3(0.2, 0, -0.3), children=[
    #         Node(15, 'ring3', humanoid_bone=HumanoidBone.leftRingDistal, Transform.from_translation(glm.vec3(0.3, 0, -0.3), children=[
    #             Node(16, 'ring4', Transform.from_translation(glm.vec3(0.4, 0, -0.3))
    #         ])
    #     ])
    # ]),
    # Node(17, 'little1', humanoid_bone=HumanoidBone.leftLittleProximal, Transform.from_translation(glm.vec3(0.1, 0, -0.4), children=[
    #     Node(18, 'little2', humanoid_bone=HumanoidBone.leftLittleIntermediate, Transform.from_translation(glm.vec3(0.2, 0, -0.4), children=[
    #         Node(19, 'little3', humanoid_bone=HumanoidBone.leftLittleDistal, Transform.from_translation(glm.vec3(0.3, 0, -0.4), children=[
    #             Node(20, 'little4', Transform.from_translation(glm.vec3(0.4, 0, -0.4))
    #         ])
    #     ])
    # ]),
    # ])

    return root
