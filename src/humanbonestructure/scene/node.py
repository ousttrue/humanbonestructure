from typing import Optional, Iterable, List, Tuple, Callable, Dict
import math
import logging
import glm
from ..humanoid.transform import Transform, trs_matrix
from ..humanoid.humanoid_bones import HumanoidBone
from ..humanoid.pose import Pose, BonePose
from ..humanoid.bone import Skeleton, BodyBones, LegBones, ArmBones, FingerBones, Joint, TR

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

    def __init__(self, name: str, local_trs: Transform, humanoid_bone: HumanoidBone = HumanoidBone.unknown,
                 *, children: Optional[List['Node']] = None) -> None:
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
        assert humanoid_bone
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

        if self.humanoid_bone == HumanoidBone.hips:
            pass

        tail_humanoid_bone = self.humanoid_bone.get_tail()
        if tail_humanoid_bone != HumanoidBone.unknown:
            tail = self.find_humanoid_bone(tail_humanoid_bone)
            if tail:
                self.humanoid_tail = tail
                return tail

        match self.humanoid_bone:
            case HumanoidBone.leftFoot | HumanoidBone.rightFoot:
                LOGGER.warn(f'no tail: {self}')
                pos = self.world_matrix[3].xyz
                end = glm.vec3(pos.x, 0, pos.z)
                local_end = glm.inverse(self.world_matrix) * end
                tail = Node('heal', Transform(local_end, glm.quat(),
                            glm.vec3(1)), HumanoidBone.endSite)
                self.add_child(tail)
                self.humanoid_tail = tail
                return tail
            case HumanoidBone.head:
                # add dummy tail
                LOGGER.warn(f'no tail: {self}')
                head_pos = self.world_matrix[3].xyz
                head_end = head_pos + glm.vec3(0, 0.2, 0)
                local_end = glm.inverse(self.world_matrix) * head_end
                tail = Node(self.name+'先', Transform(local_end,
                            glm.quat(), glm.vec3(1)), HumanoidBone.endSite)
                self.add_child(tail)
                self.humanoid_tail = tail
                return tail

       # mmd
        match self.name:
            case '下半身' | '頭':
                return next(iter(node for node, _ in self.traverse_node_and_parent() if node.name == self.name + '先'))

        if tail_humanoid_bone == HumanoidBone.endSite:
            if self.children:
                tail = self.children[0]
                self.humanoid_tail = tail
                return tail

        # add dummy tail
        LOGGER.warn(f'no tail: {self}')
        tail = Node(self.name+'先', Transform(glm.vec3(0,
                    0, 0.05), glm.quat(), glm.vec3(1)), HumanoidBone.endSite)
        self.add_child(tail)
        self.humanoid_tail = tail
        return tail

    def clear_pose(self):
        for node, _ in self.traverse_node_and_parent():
            node.pose = None

    def clear_local_axis(self):
        for node, _ in self.traverse_node_and_parent():
            node.local_axis = glm.quat()

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

    def init_human_bones(self) -> bool:
        '''
        setup humanoid bone tail
        '''
        has = False
        if self.humanoid_bone.is_enable():
            has = True
            self.humanoid_tail = self.find_tail()

        if self.children:
            for child in self.children:
                if child.init_human_bones():
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

    def calc_world_matrix(self, parent: glm.mat4):
        self.world_matrix = parent * self._get_local()
        for child in self.children:
            child.calc_world_matrix(self.world_matrix)

    def copy_tree(self) -> 'Node':
        node = Node(self.name, self.init_trs,
                    humanoid_bone=self.humanoid_bone)

        for child in self.children:
            child_copy = child.copy_tree()
            node.add_child(child_copy)

        return node

    def create_relative_pose(self, tpose_delta_map: Dict[HumanoidBone, glm.quat], *, inverted_pelvis=False) -> Pose:
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

    def to_pose(self, name='pose'):
        pose = Pose(name)
        for node, _ in self.traverse_node_and_parent(only_human_bone=True):
            if node.pose:
                pose.bones.append(
                    BonePose(node.name, node.humanoid_bone, node.pose))
        return pose

    def print_tree(self, indent=''):
        tail = 'None'
        if self.humanoid_tail:
            def f3(p: glm.vec3):
                return f'[{p.x:.3f}, {p.y:.3f}, {p.z:.3f}]'
            tail = f'{self.humanoid_tail.humanoid_bone}({self.humanoid_tail.name}): {f3(glm.normalize(self.humanoid_tail.init_trs.translation))}'
        if self.humanoid_bone.is_enable():
            print(f'{indent}{self.humanoid_bone}({self.name}) => {tail}')
        for child in self.children:
            child.print_tree(indent + '  ')

    def to_skeleton(self) -> Skeleton:
        self.calc_world_matrix(glm.mat4())
        self.print_tree()

        def node_to_joint(node: Node, parent: Optional[Joint] = None) -> Joint:
            if parent:
                m = glm.inverse(parent.world.get_matrix()) * node.world_matrix
                child = Joint(node.name, TR.from_matrix(m), node.humanoid_bone)
                parent.add_child(child)
                return child
            else:
                return Joint(node.name,
                             TR(node.init_trs.translation,
                                node.init_trs.rotation),
                             node.humanoid_bone,
                             world=TR.from_matrix(node.world_matrix))

        def create_end(parent: Joint, get_pos) -> Joint:
            world_pos = parent.world.translation
            world_end_pos = get_pos(world_pos)
            local_end_pos = glm.inverse(
                parent.world.get_matrix()) * world_end_pos
            end = Joint(f'{parent.name}_end', TR(
                local_end_pos, glm.quat()), HumanoidBone.endSite)
            parent.add_child(end)
            end.calc_world(parent.world)
            return end

        hips = node_to_joint(self[HumanoidBone.hips])
        spine = node_to_joint(self[HumanoidBone.spine], hips)
        chest = node_to_joint(self[HumanoidBone.chest], spine)
        neck = node_to_joint(self[HumanoidBone.neck], chest)
        head = node_to_joint(self[HumanoidBone.head], neck)
        head_end = create_end(head, lambda pos: pos + glm.vec3(0, 0.2, 0))
        body = BodyBones.create(hips, spine, chest, neck, head, head_end)

        left_upper_leg = node_to_joint(
            self[HumanoidBone.leftUpperLeg], hips)
        left_lower_leg = node_to_joint(
            self[HumanoidBone.leftLowerLeg], left_upper_leg)
        left_foot = node_to_joint(
            self[HumanoidBone.leftFoot], left_lower_leg)
        left_toes = node_to_joint(self[HumanoidBone.leftToes], left_foot)
        left_toes_end = create_end(
            left_toes, lambda pos: pos + glm.vec3(0, 0, 0.1))
        left_leg = LegBones.create(
            left_upper_leg, left_lower_leg, left_foot, left_toes, left_toes_end)

        right_upper_leg = node_to_joint(
            self[HumanoidBone.rightUpperLeg], hips)
        right_lower_leg = node_to_joint(
            self[HumanoidBone.rightLowerLeg], right_upper_leg)
        right_foot = node_to_joint(
            self[HumanoidBone.rightFoot], right_lower_leg)
        right_toes = node_to_joint(
            self[HumanoidBone.rightToes], right_foot)
        right_toes_end = create_end(
            right_toes, lambda pos: pos+glm.vec3(0, 0, 0.1))
        right_leg = LegBones.create(
            right_upper_leg, right_lower_leg, right_foot, right_toes, right_toes_end)

        #
        left_shoulder = node_to_joint(
            self[HumanoidBone.leftShoulder], chest)
        left_upper_arm = node_to_joint(
            self[HumanoidBone.leftUpperArm], left_shoulder)
        left_lower_arm = node_to_joint(
            self[HumanoidBone.leftLowerArm], left_upper_arm)
        left_hand = node_to_joint(
            self[HumanoidBone.leftHand], left_lower_arm)

        left_thumb_proximal = node_to_joint(
            self[HumanoidBone.leftThumbProximal], left_hand)
        left_thumb_intermediate = node_to_joint(
            self[HumanoidBone.leftThumbIntermediate], left_thumb_proximal)
        left_thumb_distal = node_to_joint(
            self[HumanoidBone.leftThumbDistal], left_thumb_intermediate)
        left_thumb_end = node_to_joint(
            self[HumanoidBone.leftThumbDistal].children[0], left_thumb_distal)
        left_thumb = FingerBones.create(
            left_thumb_proximal, left_thumb_intermediate, left_thumb_distal, left_thumb_end)

        left_index_proximal = node_to_joint(
            self[HumanoidBone.leftIndexProximal], left_hand)
        left_index_intermediate = node_to_joint(
            self[HumanoidBone.leftIndexIntermediate], left_index_proximal)
        left_index_distal = node_to_joint(
            self[HumanoidBone.leftIndexDistal], left_index_intermediate)
        left_index_end = node_to_joint(
            self[HumanoidBone.leftIndexDistal].children[0], left_index_distal)
        left_index = FingerBones.create(
            left_index_proximal, left_index_intermediate, left_index_distal, left_index_end)

        left_middle_proximal = node_to_joint(
            self[HumanoidBone.leftMiddleProximal], left_hand)
        left_middle_intermediate = node_to_joint(
            self[HumanoidBone.leftMiddleIntermediate], left_middle_proximal)
        left_middle_distal = node_to_joint(
            self[HumanoidBone.leftMiddleDistal], left_middle_intermediate)
        left_middle_end = node_to_joint(
            self[HumanoidBone.leftMiddleDistal].children[0], left_middle_distal)
        left_middle = FingerBones.create(
            left_middle_proximal, left_middle_intermediate, left_middle_distal, left_middle_end)

        left_ring_proximal = node_to_joint(
            self[HumanoidBone.leftRingProximal], left_hand)
        left_ring_intermediate = node_to_joint(
            self[HumanoidBone.leftRingIntermediate], left_ring_proximal)
        left_ring_distal = node_to_joint(
            self[HumanoidBone.leftRingDistal], left_ring_intermediate)
        left_ring_end = node_to_joint(
            self[HumanoidBone.leftRingDistal].children[0], left_ring_distal)
        left_ring = FingerBones.create(
            left_ring_proximal, left_ring_intermediate, left_ring_distal, left_ring_end)

        left_little_proximal = node_to_joint(
            self[HumanoidBone.leftLittleProximal], left_hand)
        left_little_intermediate = node_to_joint(
            self[HumanoidBone.leftLittleIntermediate], left_little_proximal)
        left_little_distal = node_to_joint(
            self[HumanoidBone.leftLittleDistal], left_little_intermediate)
        left_little_end = node_to_joint(
            self[HumanoidBone.leftLittleDistal].children[0], left_little_distal)
        left_little = FingerBones.create(
            left_little_proximal, left_little_intermediate, left_little_distal, left_little_end)

        left_arm = ArmBones.create(
            left_shoulder, left_upper_arm, left_lower_arm, left_hand,
            thumb=left_thumb,
            index=left_index,
            middle=left_middle,
            ring=left_ring,
            little=left_little
        )

        #
        right_shoulder = node_to_joint(
            self[HumanoidBone.rightShoulder], chest)
        right_upper_arm = node_to_joint(
            self[HumanoidBone.rightUpperArm], right_shoulder)
        right_lower_arm = node_to_joint(
            self[HumanoidBone.rightLowerArm], right_upper_arm)
        right_hand = node_to_joint(
            self[HumanoidBone.rightHand], right_lower_arm)
        right_thumb_proximal = node_to_joint(
            self[HumanoidBone.rightThumbProximal], right_hand)
        right_thumb_intermediate = node_to_joint(
            self[HumanoidBone.rightThumbIntermediate], right_thumb_proximal)
        right_thumb_distal = node_to_joint(
            self[HumanoidBone.rightThumbDistal], right_thumb_intermediate)
        right_thumb_end = node_to_joint(
            self[HumanoidBone.rightThumbDistal].children[0], right_thumb_distal)
        right_thumb = FingerBones.create(
            right_thumb_proximal, right_thumb_intermediate, right_thumb_distal, right_thumb_end)

        right_index_proximal = node_to_joint(
            self[HumanoidBone.rightIndexProximal], right_hand)
        right_index_intermediate = node_to_joint(
            self[HumanoidBone.rightIndexIntermediate], right_index_proximal)
        right_index_distal = node_to_joint(
            self[HumanoidBone.rightIndexDistal], right_index_intermediate)
        right_index_end = node_to_joint(
            self[HumanoidBone.rightIndexDistal].children[0], right_index_distal)
        right_index = FingerBones.create(
            right_index_proximal, right_index_intermediate, right_index_distal, right_index_end)

        right_middle_proximal = node_to_joint(
            self[HumanoidBone.rightMiddleProximal], right_hand)
        right_middle_intermediate = node_to_joint(
            self[HumanoidBone.rightMiddleIntermediate], right_middle_proximal)
        right_middle_distal = node_to_joint(
            self[HumanoidBone.rightMiddleDistal], right_middle_intermediate)
        right_middle_end = node_to_joint(
            self[HumanoidBone.rightMiddleDistal].children[0], right_middle_distal)
        right_middle = FingerBones.create(
            right_middle_proximal, right_middle_intermediate, right_middle_distal, right_middle_end)

        right_ring_proximal = node_to_joint(
            self[HumanoidBone.rightRingProximal], right_hand)
        right_ring_intermediate = node_to_joint(
            self[HumanoidBone.rightRingIntermediate], right_ring_proximal)
        right_ring_distal = node_to_joint(
            self[HumanoidBone.rightRingDistal], right_ring_intermediate)
        right_ring_end = node_to_joint(
            self[HumanoidBone.rightRingDistal].children[0], right_ring_distal)
        right_ring = FingerBones.create(
            right_ring_proximal, right_ring_intermediate, right_ring_distal, right_ring_end)

        right_little_proximal = node_to_joint(
            self[HumanoidBone.rightLittleProximal], right_hand)
        right_little_intermediate = node_to_joint(
            self[HumanoidBone.rightLittleIntermediate], right_little_proximal)
        right_little_distal = node_to_joint(
            self[HumanoidBone.rightLittleDistal], right_little_intermediate)
        right_little_end = node_to_joint(
            self[HumanoidBone.rightLittleDistal].children[0], right_little_distal)
        right_little = FingerBones.create(
            right_little_proximal, right_little_intermediate, right_little_distal, right_little_end)

        right_arm = ArmBones.create(
            right_shoulder, right_upper_arm, right_lower_arm, right_hand,
            thumb=right_thumb,
            index=right_index,
            middle=right_middle,
            ring=right_ring,
            little=right_little
        )

        return Skeleton(body,
                        left_leg, right_leg,
                        left_arm, right_arm
                        )
