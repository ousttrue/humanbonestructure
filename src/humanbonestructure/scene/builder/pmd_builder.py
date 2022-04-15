import glm
from ...formats import pmd_loader, bytesreader, buffer_types
from ..scene import Scene, Node
from ..mesh_renderer import MeshRenderer


def build(self: Scene, pmd: pmd_loader.Pmd):
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
    vertices = (buffer_types.Vertex4BoneWeights * len(pmd.vertices))()
    # skining_info = (SkinningInfo * len(pmd.vertices))()
    for i, v in enumerate(pmd.vertices):
        vv = v.render
        o = v.option
        dst = vertices[i]
        dst.position = vv.position.reverse_z()
        dst.normal = vv.normal.reverse_z()
        dst.uv = vv.uv
        dst.bone = buffer_types.Float4(o.bone0, o.bone1, 0, 0)
        w = o.weight * 0.01
        dst.weight = buffer_types.Float4(w, 1-w, 0, 0)

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
        vertices, pmd.indices, joints=self.nodes, flip=True)
