import glm
from ..node import Node
from ...formats.humanoid_bones import HumanoidBone
from ...formats.transform import Transform


def create_hand() -> Node:
    root = Node(0, 'root',  Transform.identity(), humanoid_bone=HumanoidBone.leftHand, children=[
        Node(1, 'thumb1', Transform(glm.vec3(0.1, 0, 0), glm.quat(), glm.vec3(1)), humanoid_bone=HumanoidBone.leftThumbProximal, children=[
            Node(2, 'thumb2', Transform(glm.vec3(0.1, 0, 0), glm.quat(), glm.vec3(1)), humanoid_bone=HumanoidBone.leftThumbIntermediate, children=[
                Node(3, 'thumb3', Transform(glm.vec3(0.1, 0, 0), glm.quat(), glm.vec3(1)), humanoid_bone=HumanoidBone.leftThumbDistal, children=[
                    Node(4, 'thumb4', Transform(glm.vec3(0.1, 0, 0), glm.quat(), glm.vec3(1)))
                ])
            ])
        ]),
        # Node(5, 'index1', humanoid_bone=HumanoidBone.leftIndexProximal, Transform(glm.vec3(0.1, 0, -0.1), children=[
        #     Node(6, 'index2', humanoid_bone=HumanoidBone.leftIndexIntermediate, Transform(glm.vec3(0.2, 0, -0.1), children=[
        #         Node(7, 'index3', humanoid_bone=HumanoidBone.leftIndexDistal, Transform(glm.vec3(0.3, 0, -0.1), children=[
        #             Node(8, 'index4', Transform(glm.vec3(0.4, 0, -0.1))
        #         ])
        #     ])
        # ]),
        # Node(9, 'middle1', humanoid_bone=HumanoidBone.leftMiddleProximal, Transform(glm.vec3(0.1, 0, -0.2), children=[
        #     Node(10, 'middle2', humanoid_bone=HumanoidBone.leftMiddleIntermediate, Transform(glm.vec3(0.2, 0, -0.2), children=[
        #         Node(11, 'middle3', humanoid_bone=HumanoidBone.leftMiddleDistal, Transform(glm.vec3(0.3, 0, -0.2), children=[
        #             Node(12, 'middle4', Transform(glm.vec3(0.4, 0, -0.2))
        #         ])
        #     ])
        # ]),
        # Node(13, 'ring1', humanoid_bone=HumanoidBone.leftRingProximal, Transform(glm.vec3(0.1, 0, -0.3), children=[
        #     Node(14, 'ring2', humanoid_bone=HumanoidBone.leftRingIntermediate, Transform(glm.vec3(0.2, 0, -0.3), children=[
        #         Node(15, 'ring3', humanoid_bone=HumanoidBone.leftRingDistal, Transform(glm.vec3(0.3, 0, -0.3), children=[
        #             Node(16, 'ring4', Transform(glm.vec3(0.4, 0, -0.3))
        #         ])
        #     ])
        # ]),
        # Node(17, 'little1', humanoid_bone=HumanoidBone.leftLittleProximal, Transform(glm.vec3(0.1, 0, -0.4), children=[
        #     Node(18, 'little2', humanoid_bone=HumanoidBone.leftLittleIntermediate, Transform(glm.vec3(0.2, 0, -0.4), children=[
        #         Node(19, 'little3', humanoid_bone=HumanoidBone.leftLittleDistal, Transform(glm.vec3(0.3, 0, -0.4), children=[
        #             Node(20, 'little4', Transform(glm.vec3(0.4, 0, -0.4))
        #         ])
        #     ])
        # ]),
    ])

    return root
