import glm
from ..scene import Scene, Node
from ...formats.humanoid_bones import HumanoidBone


def create_hand(scene: Scene):
    root = Node(0, 'root', humanoid_bone=HumanoidBone.leftHand, position=glm.vec3(0), children=[
        Node(1, 'thumb1', humanoid_bone=HumanoidBone.leftThumbProximal, position=glm.vec3(0.1, 0, 0), children=[
            Node(2, 'thumb2', humanoid_bone=HumanoidBone.leftThumbIntermediate, position=glm.vec3(0.2, 0, 0), children=[
                Node(3, 'thumb3', humanoid_bone=HumanoidBone.leftThumbDistal, position=glm.vec3(0.3, 0, 0), children=[
                    Node(4, 'thumb4', position=glm.vec3(0.4, 0, 0))
                ])
            ])
        ]),
        Node(5, 'index1', humanoid_bone=HumanoidBone.leftIndexProximal, position=glm.vec3(0.1, 0, -0.1), children=[
            Node(6, 'index2', humanoid_bone=HumanoidBone.leftIndexIntermediate, position=glm.vec3(0.2, 0, -0.1), children=[
                Node(7, 'index3', humanoid_bone=HumanoidBone.leftIndexDistal, position=glm.vec3(0.3, 0, -0.1), children=[
                    Node(8, 'index4', position=glm.vec3(0.4, 0, -0.1))
                ])
            ])
        ]),
        Node(9, 'middle1', humanoid_bone=HumanoidBone.leftMiddleProximal, position=glm.vec3(0.1, 0, -0.2), children=[
            Node(10, 'middle2', humanoid_bone=HumanoidBone.leftMiddleIntermediate, position=glm.vec3(0.2, 0, -0.2), children=[
                Node(11, 'middle3', humanoid_bone=HumanoidBone.leftMiddleDistal, position=glm.vec3(0.3, 0, -0.2), children=[
                    Node(12, 'middle4', position=glm.vec3(0.4, 0, -0.2))
                ])
            ])
        ]),
        Node(13, 'ring1', humanoid_bone=HumanoidBone.leftRingProximal, position=glm.vec3(0.1, 0, -0.3), children=[
            Node(14, 'ring2', humanoid_bone=HumanoidBone.leftRingIntermediate, position=glm.vec3(0.2, 0, -0.3), children=[
                Node(15, 'ring3', humanoid_bone=HumanoidBone.leftRingDistal, position=glm.vec3(0.3, 0, -0.3), children=[
                    Node(16, 'ring4', position=glm.vec3(0.4, 0, -0.3))
                ])
            ])
        ]),
        Node(17, 'little1', humanoid_bone=HumanoidBone.leftLittleProximal, position=glm.vec3(0.1, 0, -0.4), children=[
            Node(18, 'little2', humanoid_bone=HumanoidBone.leftLittleIntermediate, position=glm.vec3(0.2, 0, -0.4), children=[
                Node(19, 'little3', humanoid_bone=HumanoidBone.leftLittleDistal, position=glm.vec3(0.3, 0, -0.4), children=[
                    Node(20, 'little4', position=glm.vec3(0.4, 0, -0.4))
                ])
            ])
        ]),
    ])

    scene.nodes = [node for node, parent in root.traverse_node_and_parent()]
    scene.roots.append(root)
