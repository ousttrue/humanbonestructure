from typing import Optional, Iterable, List, Tuple, Callable, Dict
import logging
import glm
from .transform import Transform, trs_matrix

LOGGER = logging.getLogger(__name__)
NODE_ID = 1


class Node:
    '''
    SkinnigMatrix = WorldMatrix x InvereBindMatrix
    WorldMatrix = Root x ... x Parent x Local
    Local = Init x Delta x Pose

    # not propagate hierarchy
    Pose = inv(local_axis) x Pose
    '''

    def __init__(self, name: str, local_trs: Transform, *, children: Optional[List['Node']] = None) -> None:
        global NODE_ID
        self.index = NODE_ID
        NODE_ID += 1

        self.name = name
        self.children = children[:] if children else []
        self.parent: Optional[Node] = None
        assert isinstance(local_trs, Transform)
        self.init_trs = local_trs

        self.world_matrix = glm.mat4()
        self.bind_matrix = glm.mat4()

        # renderer
        from ..scene.mesh_renderer import MeshRenderer
        self.renderer: Optional[MeshRenderer] = None
        # UI
        self.has_weighted_vertices = False
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

    def clear_pose(self):
        for node, _ in self.traverse_node_and_parent():
            node.pose = None

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

    def add_child(self, child: 'Node', *, insert=False):
        if child.parent:
            child.parent.children.remove(child)
        if insert:
            self.children.insert(0, child)
        else:
            self.children.append(child)
        child.parent = self

    def calc_bind_matrix(self, parent: glm.mat4):
        self.bind_matrix = parent * self.init_trs.to_matrix()
        for child in self.children:
            child.calc_bind_matrix(self.bind_matrix)

    def _get_local(self) -> glm.mat4:
        assert self.init_trs

        t, r, s = self.init_trs
        if self.pose:
            return trs_matrix(t + self.pose.translation, r * self.pose.rotation, s * self.pose.scale)
        else:
            return trs_matrix(t, r, s)

    def calc_world_matrix(self, parent: glm.mat4):
        self.world_matrix = parent * self._get_local()
        for child in self.children:
            child.calc_world_matrix(self.world_matrix)

    def copy_tree(self) -> 'Node':
        node = Node(self.name, self.init_trs)

        for child in self.children:
            child_copy = child.copy_tree()
            node.add_child(child_copy)

        return node
