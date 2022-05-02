from typing import Optional, Iterable, List, Tuple, Callable, Dict
import math
import logging
import glm
from ..formats.transform import Transform
from ..formats.humanoid_bones import HumanoidBone
from ..formats.pose import Pose, BonePose

LOGGER = logging.getLogger(__name__)


def trs_matrix(t: glm.vec3, r: glm.quat, s: glm.vec3) -> glm.mat4:
    T = glm.translate(t)
    R = glm.mat4(r)
    S = glm.scale(s)
    m = T * R * S
    return m


NODE_ID = 1


class Node:
    '''
    SkinnigMatrix = WorldMatrix x InvereBindMatrix
    WorldMatrix = Root x ... x Parent x Local
    Local = Init x Delta x Pose

    # not propagate hierarchy
    Pose = inv(local_axis) x Pose
    '''

    def __init__(self, name: str, local_trs: Transform, *,
                 humanoid_bone: HumanoidBone = HumanoidBone.unknown,
                 children: Optional[List['Node']] = None) -> None:
        assert humanoid_bone
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
        self.delta = glm.quat()
        self.local_axis = glm.quat()
        # renderer
        from .mesh_renderer import MeshRenderer
        self.renderer: Optional[MeshRenderer] = None
        # UI
        self.has_weighted_vertices = False
        self.humanoid_bone = humanoid_bone
        self.humanoid_tail: Optional[Node] = None
        self.descendants_has_humanoid = False
        # skinning
        self.pose: Optional[Transform] = None

        for node, parent in self.traverse_node_and_parent():
            if parent:
                node.parent = parent

    def traverse_node_and_parent(self, parent: Optional['Node'] = None, *, only_human_bone=False) -> Iterable[Tuple['Node', Optional['Node']]]:
        if not only_human_bone or self.humanoid_bone.is_enable():
            yield self, parent
        for child in self.children:
            for x, y in child.traverse_node_and_parent(self, only_human_bone=only_human_bone):
                yield x, y

    def find(self, pred: Callable[['Node'], bool]) -> Optional['Node']:
        for node, _ in self.traverse_node_and_parent():
            if pred(node):
                return node

    def find_humanoid_bone(self, humanoid_bone: HumanoidBone) -> Optional['Node']:
        return self.find(lambda x: x.humanoid_bone == humanoid_bone)

    def __getitem__(self, key: HumanoidBone) -> 'Node':
        found = self.find_humanoid_bone(key)
        if not found:
            raise KeyError(key)
        return found

    def find_tail(self) -> Optional['Node']:
        assert self.humanoid_bone.is_enable()
        if not len(self.children):
            # add dummy tail
            LOGGER.warn(f'no tail: {self}')
            tail = Node(self.name+'先', Transform(glm.vec3(0,
                        0, 0.05), glm.quat(), glm.vec3(1)))
            self.add_child(tail)
            self.humanoid_tail = tail
            return tail

        human_bones = []
        for child in self.children:
            for x, _ in child.traverse_node_and_parent():
                if x.humanoid_bone.is_enable():
                    human_bones.append(x)
                    break

        if not human_bones:
            return self.children[0]
        elif len(human_bones) == 1:
            return human_bones[0]
        else:
            # mmd
            match self.name:
                case '下半身' | '頭':
                    return next(iter(node for node, _ in self.traverse_node_and_parent() if node.name == self.name + '先'))

            match self.humanoid_bone:
                case HumanoidBone.chest | HumanoidBone.upperChest:
                    for x, _ in self.traverse_node_and_parent():
                        if x.humanoid_bone == HumanoidBone.neck:
                            return x
                case HumanoidBone.rightHand:
                    for x, _ in self.traverse_node_and_parent():
                        if x.humanoid_bone == HumanoidBone.rightMiddleProximal:
                            return x
                case HumanoidBone.leftHand:
                    for x, _ in self.traverse_node_and_parent():
                        if x.humanoid_bone == HumanoidBone.leftMiddleProximal:
                            return x
                case _:
                    pass

            if self.humanoid_bone == HumanoidBone.head:
                # leftEye, rightEye, jaw is not expected
                LOGGER.warn(f'no tail: {self}')
                tail = Node('head tail', Transform(glm.vec3(0,
                            0.18, 0), glm.quat(), glm.vec3(1)))
                self.add_child(tail)
                self.humanoid_tail = tail
                return tail
            else:
                for child in self.children:
                    for node, _ in child.traverse_node_and_parent():
                        if node.humanoid_bone.is_enable():
                            return node

            return human_bones[0]

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

    def initialize(self, parent: glm.mat4) -> bool:
        self.bind_matrix = parent * trs_matrix(*self.init_trs)

        has = False
        if self.humanoid_bone.is_enable():
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

    def copy_tree(self) -> 'Node':
        node = Node(self.name, self.init_trs,
                    humanoid_bone=self.humanoid_bone)

        for child in self.children:
            child_copy = child.copy_tree()
            node.add_child(child_copy)

        return node

    def create_relative_pose(self, tpose_delta_map: Dict[HumanoidBone, glm.quat], *, inverted_pelvis=False) -> Pose:
        print('#')
        pose = Pose(self.name)

        # convert pose relative from TPose
        for node, _ in self.traverse_node_and_parent(only_human_bone=True):
            if node.pose:
                if inverted_pelvis and node.humanoid_bone == HumanoidBone.spine:
                    sp_r = glm.inverse(node.init_trs.rotation) * \
                        glm.mat(node.local_matrix)
                    p = glm.inverse(node.local_axis) * \
                        sp_r * node.local_axis
                else:
                    p = glm.inverse(node.local_axis) * \
                        node.pose.rotation * node.local_axis
            else:
                p = glm.quat()

            r = glm.inverse(tpose_delta_map[node.humanoid_bone]) * p
            angle = 180 * glm.angle(r)/math.pi
            if angle > 10:
                print(f'{node.humanoid_bone}: {angle:.2f}')
            pose.bones.append(
                BonePose(node.name, node.humanoid_bone, Transform.from_rotation(r)))

        return pose
