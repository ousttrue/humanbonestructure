from typing import List, Dict
import glm
from ...formats import pmx_loader, pmd_loader
from ...formats.transform import Transform
from ...formats.humanoid_bones import HumanoidBone
from ..node import Node
from ..mesh_renderer import MeshRenderer
from .pmd_builder import reverse_z


def build(pmx: pmx_loader.Pmx) -> Node:
    root = Node('__root__',  Transform.identity())

    # build node hierarchy
    nodes: List[Node] = []
    for i, b in enumerate(pmx.bones):
        node = Node(b.name_ja, Transform.identity())
        node.has_weighted_vertices = i in pmx.deform_bones
        nodes.append(node)

    bone_map: Dict[HumanoidBone, Node] = {}
    for i, (node, bone) in enumerate(zip(nodes, pmx.bones)):
        assert isinstance(bone, pmx_loader.Bone)
        node.humanoid_bone = pmd_loader.BONE_HUMANOID_MAP.get(
            node.name, HumanoidBone.unknown)
        if node.humanoid_bone.is_enable():
            bone_map[node.humanoid_bone] = node

        t = glm.vec3(*bone.position)
        if bone.parent_index == -1:
            node.init_trs = node.init_trs._replace(translation=reverse_z(t))
            root.add_child(node)
        else:
            t -= glm.vec3(*pmx.bones[bone.parent_index].position)
            node.init_trs = node.init_trs._replace(translation=reverse_z(t))
            parent = nodes[bone.parent_index]
            parent.add_child(node)

        if bone.tail_position:
            node.add_child(
                Node(f'{bone.name_ja}先', Transform(reverse_z(glm.vec3(*bone.tail_position)), glm.quat(), glm.vec3(1))))

    leftUpperLegD = root.find(lambda x: x.name == '左足D')
    leftLowerLegD = root.find(lambda x: x.name == '左ひざD')
    leftFootD = root.find(lambda x: x.name == '左足首D')
    leftToesD = root.find(lambda x: x.name == '左足先EX')
    leftTip = root.find(lambda x: x.name == '左足先EX先')
    rightUpperLegD = root.find(lambda x: x.name == '右足D')
    rightLowerLegD = root.find(lambda x: x.name == '右ひざD')
    rightFootD = root.find(lambda x: x.name == '右足首D')
    rightToesD = root.find(lambda x: x.name == '右足先EX')
    rightTip = root.find(lambda x: x.name == '右足先EX先')
    if leftUpperLegD and leftLowerLegD and leftFootD and rightUpperLegD and rightLowerLegD and rightFootD:
        def replace(humanoid_bone: HumanoidBone, node: Node, tail: Node):
            bone_map[humanoid_bone].humanoid_bone = HumanoidBone.unknown
            bone_map[humanoid_bone].humanoid_tail = None
            node.humanoid_bone = humanoid_bone
            node.humanoid_tail = tail
        replace(HumanoidBone.leftUpperLeg, leftUpperLegD, leftLowerLegD)
        replace(HumanoidBone.leftLowerLeg, leftLowerLegD, leftFootD)
        replace(HumanoidBone.leftFoot, leftFootD, leftToesD)
        replace(HumanoidBone.leftToes, leftToesD, leftTip)
        replace(HumanoidBone.rightUpperLeg, rightUpperLegD, rightLowerLegD)
        replace(HumanoidBone.rightLowerLeg, rightLowerLegD, rightFootD)
        replace(HumanoidBone.rightFoot, rightFootD, rightToesD)
        replace(HumanoidBone.rightToes, rightToesD, rightTip)

    # reverse z
    for i, v in enumerate(pmx.vertices):
        v.position = v.position.reverse_z()
        v.normal = v.normal.reverse_z()

    for i in range(0, len(pmx.indices), 3):
        i0, i1, i2 = pmx.indices[i:i+3]
        pmx.indices[i+0] = i0
        pmx.indices[i+1] = i2
        pmx.indices[i+2] = i1

    # set renderer
    root.renderer = MeshRenderer("assets/shader",
                                 pmx.vertices, pmx.indices, joints=nodes)

    return root
