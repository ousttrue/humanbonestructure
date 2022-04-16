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
    '''
    SkinnigMatrix = WorldMatrix x InvereBindMatrix
    WorldMatrix = Root x ... x Parent x Local
    Local = Init x Delta x Pose
    '''

    def __init__(self, index: int, name: str, local_trs: Transform, *,
                 humanoid_bone: Optional[HumanoidBone] = None,
                 children: Optional[List['Node']] = None) -> None:
        self.index = index
        self.name = name
        self.children = children[:] if children else []
        self.parent: Optional[Node] = None
        assert isinstance(local_trs, Transform)
        self.init_trs = local_trs

        self.world_matrix = glm.mat4()
        self.bind_matrix = glm.mat4()
        self.delta = glm.quat()
        # renderer
        from .mesh_renderer import MeshRenderer
        self.renderer: Optional[MeshRenderer] = None
        # UI
        self.humanoid_bone = humanoid_bone
        self.humanoid_tail: Optional[Node] = None
        self.descendants_has_humanoid = False
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
        if not len(self.children):
            return

        match self.name:
            case '上半身':
                pass
            case '上半身2':
                return next(iter(node for node, _ in self.traverse_node_and_parent() if node.name == '首'))
            case '下半身':
                return next(iter(node for node, _ in self.traverse_node_and_parent() if node.name == '下半身先'))
            case '右手首':
                return next(iter(node for node, _ in self.traverse_node_and_parent() if node.name == '右中指１'))
            case '左手首':
                return next(iter(node for node, _ in self.traverse_node_and_parent() if node.name == '左中指１'))
            case _:
                pass

        for child in self.children:
            for node, _ in child.traverse_node_and_parent():
                if node.humanoid_bone:
                    return node

        return self.children[0]

    def __str__(self) -> str:
        return f'[{self.name}: {self.init_trs}]'

    @property
    def local_matrix(self) -> glm.mat4:
        if self.parent:
            return glm.inverse(self.parent.world_matrix) * self.world_matrix
        else:
            return self.world_matrix

    @property
    def skinning_matrix(self) -> glm.mat4:
        return self.world_matrix * glm.inverse(self.bind_matrix)

    def add_child(self, child: 'Node'):
        self.children.append(child)
        child.parent = self

    def initialize(self, parent: glm.mat4) -> bool:
        self.bind_matrix = parent * trs_matrix(*self.init_trs)

        has = False
        if self.humanoid_bone:
            has = True
            self.humanoid_tail = self.find_tail()

        if self.children:
            for child in self.children:
                if child.initialize(self.bind_matrix):
                    self.descendants_has_humanoid = True
                    has = True
        return has

    def _get_local(self) -> glm.mat4:
        assert self.init_trs

        t, r, s = self.init_trs
        if self.pose:
            return trs_matrix(t + self.pose.translation, r * self.delta * self.pose.rotation, s * self.pose.scale)
        else:
            return trs_matrix(t, r * self.delta, s)

    def calc_skinning(self, parent: glm.mat4):
        self.world_matrix = parent * self._get_local()
        for child in self.children:
            child.calc_skinning(self.world_matrix)
