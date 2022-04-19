from typing import List
import glm
from ..node import Node
from ...formats.humanoid_bones import HumanoidBone
from ...formats.transform import Transform


def _create_hand(i: int, forward: glm.vec3, up: glm.vec3, thumb: glm.vec3, bones: List[HumanoidBone]) -> Node:
    fl = 0.015
    d = 0.015
    return Node(i+0, bones[0].name, Transform.from_translation(forward * fl), humanoid_bone=bones[0], children=[
        # thumb
        Node(i+1, bones[1].name, Transform.from_translation(-thumb*d-up*fl), humanoid_bone=bones[1], children=[
            Node(i+2, bones[2].name, Transform.from_translation(forward*fl*2), humanoid_bone=bones[2], children=[
                Node(i+3, bones[3].name, Transform.from_translation(forward*fl), humanoid_bone=bones[3], children=[
                    Node(i+4, bones[4].name, Transform.from_translation(forward*fl), humanoid_bone=bones[4], children=[
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


LEFT_BONES = [
    HumanoidBone.leftHand,
    HumanoidBone.leftThumbProximal,
    HumanoidBone.leftThumbIntermediate,
    HumanoidBone.leftThumbDistal,
    HumanoidBone.leftThumbTip,

    HumanoidBone.leftIndexProximal,
    HumanoidBone.leftIndexIntermediate,
    HumanoidBone.leftIndexDistal,
    HumanoidBone.leftIndexTip,

    HumanoidBone.leftMiddleProximal,
    HumanoidBone.leftMiddleIntermediate,
    HumanoidBone.leftMiddleDistal,
    HumanoidBone.leftMiddleTip,

    HumanoidBone.leftRingProximal,
    HumanoidBone.leftRingIntermediate,
    HumanoidBone.leftRingDistal,
    HumanoidBone.leftRingTip,

    HumanoidBone.leftLittleProximal,
    HumanoidBone.leftLittleIntermediate,
    HumanoidBone.leftLittleDistal,
    HumanoidBone.leftLittleTip,
]
RIGHT_BONES = [
    HumanoidBone.rightHand,
    HumanoidBone.rightThumbProximal,
    HumanoidBone.rightThumbIntermediate,
    HumanoidBone.rightThumbDistal,
    HumanoidBone.rightThumbTip,

    HumanoidBone.rightIndexProximal,
    HumanoidBone.rightIndexIntermediate,
    HumanoidBone.rightIndexDistal,
    HumanoidBone.rightIndexTip,

    HumanoidBone.rightMiddleProximal,
    HumanoidBone.rightMiddleIntermediate,
    HumanoidBone.rightMiddleDistal,
    HumanoidBone.rightMiddleTip,

    HumanoidBone.rightRingProximal,
    HumanoidBone.rightRingIntermediate,
    HumanoidBone.rightRingDistal,
    HumanoidBone.rightRingTip,

    HumanoidBone.rightLittleProximal,
    HumanoidBone.rightLittleIntermediate,
    HumanoidBone.rightLittleDistal,
    HumanoidBone.rightLittleTip,
]


def create() -> Node:
    '''
    A
    | forward
    ||||
    |||| |
    ロロ/  thumb->
    <-x
    '''
    root = Node(-1, 'root', Transform.identity())
    left = _create_hand(0, glm.vec3(1, 0, 0), glm.vec3(
        0, 1, 0), glm.vec3(0, 0, -1), LEFT_BONES)
    root.add_child(left)
    right = _create_hand(21, glm.vec3(-1, 0, 0), glm.vec3(
        0, 1, 0), glm.vec3(0, 0, -1), RIGHT_BONES)
    root.add_child(right)
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
