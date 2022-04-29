'''
厳格な TPose のヒエラルキーを生成する

* 体幹は上向き、前に曲がる
* 腕(左右)は水平向き、前に曲がる
* 脚(左右)は下向き、後ろに曲がる
* 親指以外の４指は水平向き、下に曲がる
* 親指は水平向き、後ろに曲がる
'''
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

LEFT_THUMB = [
    HumanoidBone.leftThumbProximal,
    HumanoidBone.leftThumbIntermediate,
    HumanoidBone.leftThumbDistal,
    HumanoidBone.endSite,
]

LEFT_INDEX = [
    HumanoidBone.leftIndexProximal,
    HumanoidBone.leftIndexIntermediate,
    HumanoidBone.leftIndexDistal,
    HumanoidBone.endSite,
]

LEFT_MIDDLE = [
    HumanoidBone.leftMiddleProximal,
    HumanoidBone.leftMiddleIntermediate,
    HumanoidBone.leftMiddleDistal,
    HumanoidBone.endSite,
]

LEFT_RING = [
    HumanoidBone.leftRingProximal,
    HumanoidBone.leftRingIntermediate,
    HumanoidBone.leftRingDistal,
    HumanoidBone.endSite,
]

LEFT_LITTLE = [
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

RIGHT_THUMB = [
    HumanoidBone.rightThumbProximal,
    HumanoidBone.rightThumbIntermediate,
    HumanoidBone.rightThumbDistal,
    HumanoidBone.endSite,
]

RIGHT_INDEX = [
    HumanoidBone.rightIndexProximal,
    HumanoidBone.rightIndexIntermediate,
    HumanoidBone.rightIndexDistal,
    HumanoidBone.endSite,
]

RIGHT_MIDDLE = [
    HumanoidBone.rightMiddleProximal,
    HumanoidBone.rightMiddleIntermediate,
    HumanoidBone.rightMiddleDistal,
    HumanoidBone.endSite,
]

RIGHT_RING = [
    HumanoidBone.rightRingProximal,
    HumanoidBone.rightRingIntermediate,
    HumanoidBone.rightRingDistal,
    HumanoidBone.endSite,
]

RIGHT_LITTLE = [
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

LEFT = glm.vec3(1, 0, 0)
RIGHT = glm.vec3(-1, 0, 0)
UP = glm.vec3(0, 1, 0)
DOWN = glm.vec3(0, -1, 0)


def _create(dir: glm.vec3, human_bones: List[HumanoidBone], *values) -> Node:
    bones = []
    for humanoid_bone, value in zip(human_bones, values):
        if isinstance(value, glm.vec3):
            t = value
        else:
            t = dir * value
        node = Node(humanoid_bone.name,
                    Transform.from_translation(t),
                    humanoid_bone=humanoid_bone)
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

    body = _create(UP, BODY,
                   glm.vec3(0, 0.8, 0), 0.1, 0.1, 0.2, 0.1, 0.2)

    # arms
    arms = [0.1, 0.3, 0.3, 0.05]
    body[HumanoidBone.chest].add_child(_create(
        LEFT, LEFT_ARM,
        glm.vec3(0.1, 0.2, 0), *arms))
    body[HumanoidBone.chest].add_child(_create(
        RIGHT, RIGHT_ARM,
        glm.vec3(-0.1, 0.2, 0), *arms))
    # legs
    legs = [0.4, 0.35, 0.1, 0.05]
    body[HumanoidBone.hips].add_child(_create(
        DOWN, LEFT_LEG,
        glm.vec3(0.1, 0, 0), *legs))
    body[HumanoidBone.hips].add_child(_create(
        DOWN, RIGHT_LEG,
        glm.vec3(-0.1, 0, 0), *legs))

    # fingers
    fl = 0.015
    d = 0.015
    # left
    body[HumanoidBone.leftHand].add_child(_create(
        LEFT, LEFT_THUMB,
        glm.vec3(fl, -fl, d), fl*2, fl, fl))
    body[HumanoidBone.leftHand].add_child(_create(
        LEFT, LEFT_INDEX,
        glm.vec3(fl * 3.5, 0, d), fl*2, fl, fl))
    body[HumanoidBone.leftHand].add_child(_create(
        LEFT, LEFT_MIDDLE,
        glm.vec3(fl * 4.0, 0, 0), fl*2, fl, fl))
    body[HumanoidBone.leftHand].add_child(_create(
        LEFT, LEFT_RING,
        glm.vec3(fl * 3.5, 0, -d), fl*2, fl, fl))
    body[HumanoidBone.leftHand].add_child(_create(
        LEFT, LEFT_LITTLE,
        glm.vec3(fl * 3.0, 0, -d*2), fl*2, fl, fl))
    # right
    body[HumanoidBone.rightHand].add_child(_create(
        RIGHT, RIGHT_THUMB,
        glm.vec3(-fl, -fl, d), fl*2, fl, fl))
    body[HumanoidBone.rightHand].add_child(_create(
        RIGHT, RIGHT_INDEX,
        glm.vec3(-fl * 3.5, 0, d), fl*2, fl, fl))
    body[HumanoidBone.rightHand].add_child(_create(
        RIGHT, RIGHT_MIDDLE,
        glm.vec3(-fl * 4.0, 0, 0), fl*2, fl, fl))
    body[HumanoidBone.rightHand].add_child(_create(
        RIGHT, RIGHT_RING,
        glm.vec3(-fl * 3.5, 0, -d), fl*2, fl, fl))
    body[HumanoidBone.rightHand].add_child(_create(
        RIGHT, RIGHT_LITTLE,
        glm.vec3(-fl * 3.0, 0, -d*2), fl*2, fl, fl))

    root.add_child(body)

    return root
