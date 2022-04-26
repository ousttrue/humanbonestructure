from typing import List, Dict
import ctypes
import glm
from ...formats import gltf_loader, buffer_types
from ...formats.humanoid_bones import HumanoidBone
from ...formats.transform import Transform
from ..node import Node
from ..mesh_renderer import MeshRenderer


CESIUMMAN_HUMANOID_MAP = {
    'Skeleton_torso_joint_1': HumanoidBone.hips,
    'Skeleton_torso_joint_2': HumanoidBone.spine,
    'torso_joint_3': HumanoidBone.chest,
    'Skeleton_neck_joint_1': HumanoidBone.neck,
    'Skeleton_neck_joint_2': HumanoidBone.head,
    'Skeleton_arm_joint_L__4_': HumanoidBone.leftUpperArm,
    'Skeleton_arm_joint_L__3_': HumanoidBone.leftLowerArm,
    'Skeleton_arm_joint_L__2_': HumanoidBone.leftHand,
    'Skeleton_arm_joint_R': HumanoidBone.rightUpperArm,
    'Skeleton_arm_joint_R__2_': HumanoidBone.rightLowerArm,
    'Skeleton_arm_joint_R__3_': HumanoidBone.rightHand,
    'leg_joint_L_1': HumanoidBone.leftUpperLeg,
    'leg_joint_L_2': HumanoidBone.leftLowerLeg,
    'leg_joint_L_3': HumanoidBone.leftFoot,
    'leg_joint_L_5': HumanoidBone.leftToes,
    'leg_joint_R_1': HumanoidBone.rightUpperLeg,
    'leg_joint_R_2': HumanoidBone.rightLowerLeg,
    'leg_joint_R_3': HumanoidBone.rightFoot,
    'leg_joint_R_5': HumanoidBone.rightToes,
}


def build(gltf: gltf_loader.Gltf) -> Node:

    vrm = None

    # vrm-0.x
    human_bone_map: Dict[int, HumanoidBone] = gltf.get_vrm0_human_bone_map()
    if human_bone_map:
        vrm = 0

    # vrm-1.0
    human_bone_map = gltf.get_vrm1_human_bone_map()
    if human_bone_map:
        vrm = 1

    def set_human_bone(i: int, node: Node):
        human_bone = human_bone_map.get(i)
        if human_bone:
            node.humanoid_bone = human_bone
            return

        # cesium man !
        human_bone = CESIUMMAN_HUMANOID_MAP.get(node.name)
        if human_bone:
            node.humanoid_bone = human_bone
            return

    meshes = []
    for gltf_mesh in gltf.gltf.get('meshes', []):
        vertices_len, indices_len = gltf_loader.vertices_indices_len(
            gltf.gltf, gltf_mesh)

        # merge submesh
        vertices = (buffer_types.Vertex4BoneWeights * vertices_len)()
        indices = (ctypes.c_uint16 * indices_len)()
        vertex_offset = 0
        index_offset = 0

        for prim in gltf_mesh['primitives']:
            # merge indices
            indices_accessor = prim.get('indices')
            assert isinstance(indices_accessor, int)
            sub_indices = gltf.load_accessor(indices_accessor)

            for i, src in enumerate(sub_indices):
                indices[i+index_offset] = src
            index_offset += len(sub_indices)

            # merge vertices
            attributes = [(k, gltf.load_accessor(
                v)) for k, v in prim.get('attributes', {}).items()]

            keys = {k: i for i, (k, v) in enumerate(attributes)}
            position_ref = keys['POSITION']
            normal_ref = keys['NORMAL']
            uv_ref = keys['TEXCOORD_0']
            bone_ref = keys.get('JOINTS_0')
            weight_ref = keys.get('WEIGHTS_0')
            values = [v for k, v, in attributes]

            for i, src in enumerate(zip(*values)):
                dst = vertices[vertex_offset]
                if human_bone_map:
                    dst.position = src[position_ref].rotate_y180()
                    dst.normal = src[normal_ref].rotate_y180()
                else:
                    dst.position = src[position_ref]
                    dst.normal = src[normal_ref]
                dst.uv = src[uv_ref]

                if bone_ref and weight_ref:
                    bones = src[bone_ref]
                    weights = src[weight_ref]

                    dst.bone = buffer_types.Float4(
                        bones.x, bones.y, bones.z, bones.w)
                    dst.weight = weights

                vertex_offset += 1

        assert vertex_offset == len(vertices)
        assert index_offset == len(indices)
        meshes.append((vertices, indices))

    # build hierarchy
    nodes: List[Node] = []
    for i, gltf_node in enumerate(gltf.gltf.get('nodes', [])):
        name = gltf_node.get('name', f'{i}')
        t, r, s = gltf_loader.get_trs(gltf_node)
        if vrm == 0:
            # vrm-0.x: rotate y180
            # TODO: if not normalized
            t = glm.vec3(-t.x, t.y, -t.z)
        node = Node(i, name, Transform(t, r, s))
        set_human_bone(i, node)
        nodes.append(node)

    for gltf_node, node in zip(gltf.gltf.get('nodes', []), nodes):
        for child_index in gltf_node.get('children', []):
            child = nodes[child_index]
            node.add_child(child)

        mesh_index = gltf_node.get('mesh')
        skin_index = gltf_node.get('skin')
        if isinstance(mesh_index, int):
            vertices, indices = meshes[mesh_index]
            if isinstance(skin_index, int):
                gltf_skin = gltf.gltf.get('skins', [])[skin_index]
                if gltf_skin:
                    joints = [nodes[joint]
                              for joint in gltf_skin['joints']]

                    bind_index = gltf_skin.get('inverseBindMatrices')
                    if bind_index:
                        m = gltf.load_accessor(bind_index)
                        # for m, j in zip(m, joints):
                        #     j.inverse_bind_matrix = glm.transpose(glm.mat4(
                        #         *m
                        #     ))

                    node.renderer = MeshRenderer("assets/shader",
                                                 vertices, indices, joints=joints)
                else:
                    node.renderer = MeshRenderer("assets/shader",
                                                 vertices, indices)
            else:
                node.renderer = MeshRenderer("assets/shader",
                                             vertices, indices)

    root = Node(-1, '__root__', Transform.identity())
    for node in nodes:
        if not node.parent:
            root.add_child(node)
    return root
