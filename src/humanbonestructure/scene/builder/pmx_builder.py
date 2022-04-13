import glm
from ...formats import pmx_loader, pmd_loader
from ..scene import Scene, Node
from ..mesh_renderer import MeshRenderer


def build(self: Scene, pmx: pmx_loader.Pmx):
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
