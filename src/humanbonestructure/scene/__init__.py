from typing import Optional, List
import ctypes
import pathlib
import logging
from OpenGL import GL
import glm
from pydear import imgui as ImGui
from pydear.scene.camera import Camera
from ..formats import pmd_loader, gltf_loader, vpd_loader, pmx_loader, bytesreader
from .node import Node
from .mesh_renderer import MeshRenderer
from ..formats.buffer_types import Float4, Vertex4BoneWeights
from ..formats.humanoid_bones import HumanoidBone
from .axis import Axis
from ..formats.transform import Transform
LOGGER = logging.getLogger(__name__)


class Scene:
    def __init__(self) -> None:
        # gizmo
        self.axis = Axis()
        # scene
        self.nodes: List[Node] = []
        self.roots: List[Node] = []
        # gui
        self.camera = Camera(distance=4, y=-0.8)
        self.hover = False

    def load_model(self, path: pathlib.Path):
        match path.suffix.lower():
            case '.pmd':
                self.load_pmd(path)
            case '.pmx':
                self.load_pmx(path)
            case '.glb' | '.vrm':
                self.load_glb(path)
            case _:
                raise NotImplementedError()

    def load_pmd(self, path: pathlib.Path):
        self.nodes.clear()
        self.roots.clear()

        pmd = pmd_loader.Pmd(path.read_bytes())
        LOGGER.debug(pmd)

        # build node hierarchy
        for i, b in enumerate(pmd.bones):
            node = Node(i, bytesreader.bytes_to_str(b.name), position=glm.vec3(b.position.x, b.position.y,
                                                                               -b.position.z  # reverse z
                                                                               ))
            self.nodes.append(node)

        for i, (node, bone) in enumerate(zip(self.nodes, pmd.bones)):
            if humanoid_bone := pmd_loader.BONE_HUMANOID_MAP.get(node.name):
                node.humanoid_bone = humanoid_bone

            if bone.parent_index == 65535:
                self.roots.append(node)
            else:
                parent = self.nodes[bone.parent_index]
                parent.add_child(node)

        # setup vertex and skinning
        vertices = (Vertex4BoneWeights * len(pmd.vertices))()
        # skining_info = (SkinningInfo * len(pmd.vertices))()
        for i, v in enumerate(pmd.vertices):
            vv = v.render
            o = v.option
            dst = vertices[i]
            dst.position = vv.position.reverse_z()
            dst.normal = vv.normal.reverse_z()
            dst.uv = vv.uv
            dst.bone = Float4(o.bone0, o.bone1, 0, 0)
            w = o.weight * 0.01
            dst.weight = Float4(w, 1-w, 0, 0)

            # skining_info[i] = SkinningInfo(
            #     Float3(vv.position.x, vv.position.y, vv.position.z),
            #     UShort4(o.bone0, o.bone1, 0, 0),
            #     Float4(w, 1-w, 0, 0))

        # root origin
        if self.roots[0].init_position != glm.vec3(0, 0, 0):
            root = Node(len(self.nodes), '__root__',
                        position=glm.vec3(0, 0, 0))
            for r in self.roots:
                root.add_child(r)
            self.roots = [root]

        # set renderer
        self.roots[0].renderer = MeshRenderer(
            vertices, pmd.indices, joints=self.nodes)

        # finalize
        for root in self.roots:
            root.initialize()
            root.calc_skinning(glm.mat4())

    def load_pmx(self, path: pathlib.Path):
        self.nodes.clear()
        self.roots.clear()

        pmx = pmx_loader.Pmx(path.read_bytes())
        LOGGER.debug(pmx)

        # build node hierarchy
        for i, b in enumerate(pmx.bones):
            node = Node(i, b.name_ja, position=glm.vec3(b.position.x, b.position.y,
                                                        -b.position.z  # reverse z
                                                        ))
            self.nodes.append(node)

        for i, (node, bone) in enumerate(zip(self.nodes, pmx.bones)):
            if humanoid_bone := pmd_loader.BONE_HUMANOID_MAP.get(node.name):
                node.humanoid_bone = humanoid_bone

            if bone.parent_index == -1:
                self.roots.append(node)
            else:
                parent = self.nodes[bone.parent_index]
                parent.add_child(node)

        # reverse z
        for i, v in enumerate(pmx.vertices):
            v.position = v.position.reverse_z()
            v.normal = v.normal.reverse_z()

        # root origin
        if self.roots[0].init_position != glm.vec3(0, 0, 0):
            root = Node(len(self.nodes), '__root__',
                        position=glm.vec3(0, 0, 0))
            for r in self.roots:
                root.add_child(r)
            self.roots = [root]

        # set renderer
        self.roots[0].renderer = MeshRenderer(
            pmx.vertices, pmx.indices, joints=self.nodes)

        # finalize
        for root in self.roots:
            root.initialize()
            root.calc_skinning(glm.mat4())

    def load_glb(self, path: pathlib.Path):
        self.nodes.clear()
        self.roots.clear()

        gltf = gltf_loader.Gltf.load_glb(path.read_bytes())
        LOGGER.debug(gltf)

        # vrm-0.x
        human_bone_map = gltf.get_vrm_human_bone_map()

        meshes = []
        for gltf_mesh in gltf.gltf.get('meshes', []):
            vertices_len, indices_len = gltf_loader.vertices_indices_len(
                gltf.gltf, gltf_mesh)

            # merge submesh
            vertices = (Vertex4BoneWeights * vertices_len)()
            indices = (ctypes.c_uint16 * indices_len)()
            vertex_offset = 0
            index_offset = 0
            # skinning_info = [None] * vertices_len

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
                bone_ref = keys['JOINTS_0']
                weight_ref = keys['WEIGHTS_0']
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

                    bones = src[bone_ref]
                    weights = src[weight_ref]

                    dst.bone = Float4(bones.x, bones.y, bones.z, bones.w)
                    dst.weight = weights

                    vertex_offset += 1

                # vertex_offset += len(values[0])

            assert vertex_offset == len(vertices)
            assert index_offset == len(indices)
            meshes.append((vertices, indices))

        # build hierarchy
        for i, gltf_node in enumerate(gltf.gltf.get('nodes', [])):
            name = gltf_node.get('name', f'{i}')
            t, r, s = gltf_loader.get_trs(gltf_node)
            if human_bone_map:
                # rotate y180
                t = glm.vec3(-t.x, t.y, -t.z)
            node = Node(i, name, trs=Transform(t, r, s))
            # if human_bones
            human_bone = human_bone_map.get(i)
            if human_bone:
                node.humanoid_bone = HumanoidBone(human_bone)

            self.nodes.append(node)
        for gltf_node, node in zip(gltf.gltf.get('nodes', []), self.nodes):
            for child_index in gltf_node.get('children', []):
                child = self.nodes[child_index]
                node.add_child(child)

            mesh_index = gltf_node.get('mesh')
            skin_index = gltf_node.get('skin')
            if isinstance(mesh_index, int):
                vertices, indices = meshes[mesh_index]
                if isinstance(skin_index, int):
                    gltf_skin = gltf.gltf.get('skins', [])[skin_index]
                    if gltf_skin:
                        joints = [self.nodes[joint]
                                  for joint in gltf_skin['joints']]

                        bind_index = gltf_skin.get('inverseBindMatrices')
                        if bind_index:
                            m = gltf.load_accessor(bind_index)
                            # for m, j in zip(m, joints):
                            #     j.inverse_bind_matrix = glm.transpose(glm.mat4(
                            #         *m
                            #     ))

                        node.renderer = MeshRenderer(
                            vertices, indices, joints=joints)
                    else:
                        node.renderer = MeshRenderer(
                            vertices, indices)
                else:
                    raise NotImplementedError()

        # finalize
        for node in self.nodes:
            if not node.parent:
                self.roots.append(node)

        for root in self.roots:
            root.initialize()
            root.calc_skinning(glm.mat4())

    def render(self, w: int, h: int):
        # camera update
        self.camera.onResize(w, h)
        if self.hover:
            wx, wy = ImGui.GetWindowPos()
            wy += ImGui.GetFrameHeight()
            io = ImGui.GetIO()

            x = int(io.MousePos.x-wx)
            y = int(io.MousePos.y-wy)

            if io.MouseDown[0]:
                self.camera.onLeftDown(x, y)
            else:
                self.camera.onLeftUp(x, y)

            if io.MouseDown[1]:
                self.camera.onRightDown(x, y)
            else:
                self.camera.onRightUp(x, y)

            if io.MouseDown[2]:
                self.camera.onMiddleDown(x, y)
            else:
                self.camera.onMiddleUp(x, y)

            self.camera.onMotion(x, y)
            self.camera.onWheel(int(-io.MouseWheel))

        # render
        GL.glEnable(GL.GL_DEPTH_TEST)
        for root in self.roots:
            self.render_node(root)

        self.axis.render(self.camera)

    def render_node(self, node: Node):
        if node.renderer:
            node.renderer.render(self.camera, node)

        for child in node.children:
            self.render_node(child)

    def load_vpd(self, vpd: Optional[vpd_loader.Vpd]):
        # clear
        for node in self.nodes:
            node.pose = None

        # self.vpd = Vpd(pkgutil.get_data('humanbonestructure', 'assets/Pose/右手グー.vpd'))
        self.vpd = vpd
        LOGGER.debug(self.vpd)

        humanoid_node_map = {node.humanoid_bone: node for node in self.nodes}

        # assign pose to node hierarchy
        if self.vpd:
            for bone in self.vpd.bones:
                humanoid_bone = pmd_loader.BONE_HUMANOID_MAP.get(bone.name)
                if humanoid_bone:
                    node = humanoid_node_map.get(humanoid_bone)
                    if node and node.humanoid_bone:
                        # Handより祖先に適用しない(mask)
                        if node.humanoid_bone.is_finger():
                            node.pose = bone.transform.reverse_z()
                    else:
                        LOGGER.warn(f'{bone.name} not found')

        # calc skinning matrix
        for root in self.roots:
            root.calc_skinning(glm.mat4())
