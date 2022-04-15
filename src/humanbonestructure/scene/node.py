from typing import Optional, Iterable, List, Tuple, Callable
import glm
from ..formats.transform import Transform
from ..formats.humanoid_bones import HumanoidBone


def trs_matrix(t: glm.vec3, r: glm.quat, s: glm.vec3) -> glm.mat4:
    T = glm.translate(t)
    R = glm.mat4(r)
    S = glm.scale(s)
    m = T * R * S
    return m


class Node:
    def __init__(self, index: int, name: str, *,
                 position: Optional[glm.vec3] = None,
                 trs: Optional[Transform] = None,
                 humanoid_bone: Optional[HumanoidBone] = None,
                 children: Optional[List['Node']] = None) -> None:
        self.index = index
        self.name = name
        self.children = children[:] if children else []
        self.parent: Optional[Node] = None
        self.world_matrix = glm.mat4()
        self.init_position = position
        self.init_trs = trs
        self.inverse_bind_matrix = glm.mat4()
        self.delta = glm.quat()
        # renderer
        from .mesh_renderer import MeshRenderer
        self.renderer: Optional[MeshRenderer] = None
        # UI
        self.humanoid_bone = humanoid_bone
        self.descendants_has_humaniod = False
        # skinning
        self.pose: Optional[Transform] = None

        for node, parent in self.traverse_node_and_parent():
            if parent:
                node.parent = parent

    def traverse_node_and_parent(self, parent: Optional['Node'] = None) -> Iterable[Tuple['Node', Optional['Node']]]:
        yield self, parent
        for child in self.children:
            for x, y in child.traverse_node_and_parent(self):
                yield x, y

    def find(self, pred: Callable[['Node'], bool]) -> Optional['Node']:
        for node, _ in self.traverse_node_and_parent():
            if pred(node):
                return node

    def find_tail(self) -> Optional['Node']:
        assert self.humanoid_bone
        for child in self.children:
            for node, _ in child.traverse_node_and_parent():
                if node.humanoid_bone:
                    return node
        if self.children:
            return self.children[0]

    def __str__(self) -> str:
        if self.init_position:
            return f'[{self.name}: {self.init_position}]'
        elif self.init_trs:
            return f'[{self.name}: {self.init_trs}]'
        else:
            raise NotImplementedError()

    @property
    def skinning_matrix(self) -> glm.mat4:
        return self.world_matrix * glm.mat4(glm.inverse(self.delta)) * self.inverse_bind_matrix

    def add_child(self, child: 'Node'):
        self.children.append(child)
        child.parent = self

    def initialize(self) -> bool:
        self.delta = glm.quat()
        if self.init_trs:
            # gltf
            pass
        elif self.init_position:
            # pmd / pmx
            if self.parent:
                t = self.init_position - self.parent.init_position
            else:
                t = self.init_position
            self.init_trs = Transform(t, glm.quat(), glm.vec3(1))
        else:
            raise NotImplementedError()

        if self.parent:
            self.world_matrix = self.parent.world_matrix * \
                self._get_local(init=True)
        else:
            self.world_matrix = self._get_local(init=True)

        self.inverse_bind_matrix = glm.inverse(self.world_matrix)

        has = False
        if self.humanoid_bone:
            has = True

        if self.children:
            for child in self.children:
                if child.initialize():
                    self.descendants_has_humaniod = True
                    has = True
        return has

    def _get_local(self, init=False) -> glm.mat4:
        assert self.init_trs

        t, r, s = self.init_trs
        if not init and self.pose:
            return trs_matrix(self.pose.translation + t, self.pose.rotation * r, self.pose.scale * s)
        else:
            return trs_matrix(t, r, s)

    def calc_skinning(self, parent: glm.mat4):
        self.world_matrix = parent * self._get_local()
        for child in self.children:
            child.calc_skinning(self.world_matrix)
