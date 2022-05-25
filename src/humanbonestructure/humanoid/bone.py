from typing import NamedTuple, List, Optional, Union, Iterable
from enum import Enum, auto
import glm
from .humanoid_bones import HumanoidBone, BoneBase, BoneFlags
from .coordinate import Coordinate
from .pose import Pose, BonePose
from ..scene.transform import Transform


class AxisPositiveNegative(Enum):
    XPositive = auto()
    XNegative = auto()
    YPositive = auto()
    YNegative = auto()
    ZPositive = auto()
    ZNegative = auto()


class TR(NamedTuple):
    translation: glm.vec3 = glm.vec3(0, 0, 0)
    rotation: glm.quat = glm.quat()

    @staticmethod
    def from_matrix(m: glm.mat4) -> 'TR':
        return TR(m[3].xyz, glm.quat(m))

    def get_matrix(self) -> glm.mat4:
        return glm.translate(self.translation) * glm.mat4(self.rotation)

    def __mul__(self, rhs: 'TR') -> 'TR':
        '''
        R1R2|
        '''
        return TR((self.rotation * glm.vec4(rhs.translation, 1)).xyz + self.translation, self.rotation * rhs.rotation)


class Joint:
    def __init__(self, name: str, local: TR, humanoid_bone: HumanoidBone, *, world: Optional[TR] = None, parent: Optional['Joint'] = None) -> None:
        self.name = name
        self.local = local
        self.world = world if world else local
        self.humanoid_bone = humanoid_bone
        self.pose = glm.quat()
        self.children: List[Joint] = []
        self.parent: Optional[Joint] = parent
        self.local_axis = glm.quat()
        if self.parent:
            self.parent.add_child(self)

    def get_parent_world_matrix(self) -> glm.mat4:
        return self.parent.world.get_matrix() if self.parent else glm.mat4()

    def traverse(self) -> Iterable['Joint']:
        yield self
        for child in self.children:
            for x in child.traverse():
                yield x

    def add_child(self, child: 'Joint'):
        child.parent = self
        self.children.append(child)
        child.calc_world(self.world)

    def calc_world(self, parent: TR):
        self.world = parent * self.local * TR(glm.vec3(0, 0, 0), self.pose)
        for child in self.children:
            child.calc_world(self.world)


EPSILON = 2e-2


class Bone:
    def __init__(self, head: Joint, tail: Joint) -> None:
        self.head = head
        self.tail = tail
        self.calc_axis()

    @property
    def local_axis(self) -> glm.quat:
        return self.head.local_axis

    @property
    def humanoid_bone(self) -> HumanoidBone:
        return self.head.humanoid_bone

    def get_local_tail(self) -> glm.vec3:
        # tail.local.translation
        m = self.head.world.get_matrix() * glm.mat4(self.local_axis)
        return (glm.inverse(m) * glm.vec4(self.tail.world.translation, 1)).xyz

    def get_up_dir(self) -> glm.vec3:
        m = self.head.world.get_matrix() * glm.mat4(self.local_axis)
        return (glm.inverse(m) * glm.vec4(self.head.humanoid_bone.world_second, 0)).xyz

    def calc_axis(self):

        local_tail_dir = glm.normalize(self.get_local_tail())
        if abs(local_tail_dir.x - 1) < EPSILON:
            self.head_tail_axis = AxisPositiveNegative.XPositive
        elif abs(local_tail_dir.x + 1) < EPSILON:
            self.head_tail_axis = AxisPositiveNegative.XNegative
        elif abs(local_tail_dir.y - 1) < EPSILON:
            self.head_tail_axis = AxisPositiveNegative.YPositive
        elif abs(local_tail_dir.y + 1) < EPSILON:
            self.head_tail_axis = AxisPositiveNegative.YNegative
        elif abs(local_tail_dir.z - 1) < EPSILON:
            self.head_tail_axis = AxisPositiveNegative.ZPositive
        elif abs(local_tail_dir.z + 1) < EPSILON:
            self.head_tail_axis = AxisPositiveNegative.ZNegative
        else:
            self.head_tail_axis = None

        self.second_axis = None
        if self.head_tail_axis:
            world_second = self.head.humanoid_bone.world_second
            m = glm.mat4(self.head.world.rotation * self.local_axis)
            d0 = glm.dot(m[0].xyz, world_second)
            d1 = glm.dot(m[1].xyz, world_second)
            d2 = glm.dot(m[2].xyz, world_second)
            if abs(d0) > abs(d1) and abs(d0) > abs(d2):
                if d0 > 0:
                    self.second_axis = AxisPositiveNegative.XPositive
                else:
                    self.second_axis = AxisPositiveNegative.XNegative
            elif abs(d1) > abs(d0) and abs(d1) > abs(d2):
                if d1 > 0:
                    self.second_axis = AxisPositiveNegative.YPositive
                else:
                    self.second_axis = AxisPositiveNegative.YNegative
            elif abs(d2) > abs(d0) and abs(d2) > abs(d1):
                if d2 > 0:
                    self.second_axis = AxisPositiveNegative.ZPositive
                else:
                    self.second_axis = AxisPositiveNegative.ZNegative
            else:
                raise RuntimeError()

        # if self.head_tail_axis:
        #     assert self.head_tail_axis != self.second_axis
        # else:
        #     assert self.second_axis is None

    def get_length(self) -> float:
        return glm.length(self.tail.world.translation - self.head.world.translation)

    def get_coordinate(self) -> Coordinate:
        match self.head_tail_axis, self.second_axis:
            case AxisPositiveNegative.XPositive, AxisPositiveNegative.YPositive:
                return Coordinate(
                    yaw=glm.vec3(0, 1, 0),
                    pitch=glm.vec3(0, 0, 1),
                    roll=glm.vec3(1, 0, 0),
                )
            case AxisPositiveNegative.XPositive, AxisPositiveNegative.YNegative:
                return Coordinate(
                    yaw=glm.vec3(0, -1, 0),
                    pitch=glm.vec3(0, 0, -1),
                    roll=glm.vec3(1, 0, 0),
                )
            case AxisPositiveNegative.XPositive, AxisPositiveNegative.ZPositive:
                return Coordinate(
                    yaw=glm.vec3(0, 0, 1),
                    pitch=glm.vec3(0, -1, 0),
                    roll=glm.vec3(1, 0, 0),
                )
            case AxisPositiveNegative.XPositive, AxisPositiveNegative.ZNegative:
                return Coordinate(
                    yaw=glm.vec3(0, 0, -1),
                    pitch=glm.vec3(0, 1, 0),
                    roll=glm.vec3(1, 0, 0),
                )
            case AxisPositiveNegative.YPositive, AxisPositiveNegative.ZPositive:
                return Coordinate(
                    yaw=glm.vec3(0, 0, 1),
                    pitch=glm.vec3(1, 0, 0),
                    roll=glm.vec3(0, 1, 0),
                )
            case AxisPositiveNegative.YPositive, AxisPositiveNegative.ZNegative:
                return Coordinate(
                    yaw=glm.vec3(0, 0, -1),
                    pitch=glm.vec3(-1, 0, 0),
                    roll=glm.vec3(0, 1, 0),
                )
            case AxisPositiveNegative.YNegative, AxisPositiveNegative.ZNegative:
                return Coordinate(
                    yaw=glm.vec3(0, 0, -1),
                    pitch=glm.vec3(1, 0, 0),
                    roll=glm.vec3(0, -1, 0),
                )
            case AxisPositiveNegative.XNegative, AxisPositiveNegative.YNegative:
                return Coordinate(
                    yaw=glm.vec3(0, -1, 0),
                    pitch=glm.vec3(0, 0, 1),
                    roll=glm.vec3(-1, 0, 0),
                )
            case AxisPositiveNegative.XNegative, AxisPositiveNegative.ZPositive:
                return Coordinate(
                    yaw=glm.vec3(0, 0, 1),
                    pitch=glm.vec3(0, 1, 0),
                    roll=glm.vec3(-1, 0, 0),
                )
            case AxisPositiveNegative.XNegative, AxisPositiveNegative.ZNegative:
                return Coordinate(
                    yaw=glm.vec3(0, 0, -1),
                    pitch=glm.vec3(0, -1, 0),
                    roll=glm.vec3(-1, 0, 0),
                )
            case AxisPositiveNegative.ZPositive, AxisPositiveNegative.YNegative:
                return Coordinate(
                    yaw=glm.vec3(0, -1, 0),
                    pitch=glm.vec3(1, 0, 0),
                    roll=glm.vec3(0, 0, 1),
                )
            case _:
                raise NotImplementedError()

    def calc_world_matrix(self, parent: glm.mat4) -> glm.mat4:
        m = parent * self.head.local.get_matrix() * glm.mat4(self.head.pose)
        self.head.world = TR.from_matrix(m)
        return m

    def strict_tpose(self, parent: glm.mat4):
        world = parent * self.head.local.get_matrix()
        world_axis = glm.quat(world) * self.local_axis
        # world_target = glm.mat4()
        # world * delta * local_axis = world_target
        delta = self.local_axis * \
            glm.inverse(world_axis) * glm.inverse(self.local_axis)
        self.head.pose = delta
        return self.calc_world_matrix(parent)

    def get_target_matrix(self, flag: BoneFlags) -> glm.mat4:
        match self.head.humanoid_bone.base:
            case (BoneBase.hips | BoneBase.spine | BoneBase.chest | BoneBase.neck | BoneBase.head):
                world_x = glm.vec3(1, 0, 0)
                world_y = glm.normalize(
                    self.tail.world.translation - self.head.world.translation)
                world_z = glm.normalize(glm.cross(world_x, world_y))
                return glm.mat4(
                    glm.vec4(world_x, 0),
                    glm.vec4(world_y, 0),
                    glm.vec4(world_z, 0),
                    glm.vec4(0, 0, 0, 1),
                )
            case (BoneBase.upperLeg | BoneBase.lowerLeg):
                world_x = glm.vec3(1, 0, 0)
                world_y = glm.normalize(
                    self.head.world.translation-self.tail.world.translation)
                world_z = glm.normalize(glm.cross(world_x, world_y))
                return glm.mat4(
                    glm.vec4(world_x, 0),
                    glm.vec4(world_y, 0),
                    glm.vec4(world_z, 0),
                    glm.vec4(0, 0, 0, 1),
                )
            case BoneBase.foot | BoneBase.toes | BoneBase.shoulder:
                # 元の姿勢を残す(head-tail無視)
                return glm.mat4(
                    glm.vec4(1, 0, 0, 0),
                    glm.vec4(0, 1, 0, 0),
                    glm.vec4(0, 0, 1, 0),
                    glm.vec4(0, 0, 0, 1),
                )
            case BoneBase.upperArm | BoneBase.lowerArm | BoneBase.hand | BoneBase.finger_1 | BoneBase.finger_2 | BoneBase.finger_3:
                world_y = glm.vec3(0, 1, 0)
                if flag & BoneFlags.Left:
                    world_x = glm.normalize(
                        self.tail.world.translation-self.head.world.translation)
                    world_z = glm.normalize(glm.cross(world_x, world_y))
                    world_y = glm.normalize(glm.cross(world_z, world_x))

                elif flag & BoneFlags.Right:
                    world_x = -glm.normalize(
                        self.tail.world.translation-self.head.world.translation)
                    world_z = glm.normalize(glm.cross(world_x, world_y))
                    world_y = glm.normalize(glm.cross(world_z, world_x))

                else:
                    raise RuntimeError()

                return glm.mat4(
                    glm.vec4(world_x, 0),
                    glm.vec4(world_y, 0),
                    glm.vec4(world_z, 0),
                    glm.vec4(0, 0, 0, 1),
                )
            case _:
                raise NotImplementedError()

    def cancel_axis(self):
        target = self.get_target_matrix(self.head.humanoid_bone.flags)
        self.head.local_axis = glm.inverse(
            self.head.world.rotation) * glm.quat(target)
        self.calc_axis()

    def clear_axis(self):
        self.head.local_axis = glm.quat()
        self.calc_axis()


class BodyBones(NamedTuple):
    hips: Bone
    spine: Bone
    chest: Bone
    neck: Bone
    head: Bone

    def enumerate(self) -> Iterable[Bone]:
        yield self.hips
        yield self.spine
        yield self.chest
        yield self.neck
        yield self.head

    @staticmethod
    def create(hips: Joint, spine: Joint, chest: Joint, neck: Joint, head: Joint, end: Joint) -> 'BodyBones':
        return BodyBones(
            Bone(hips, spine),
            Bone(spine, chest),
            Bone(chest, neck),
            Bone(neck, head),
            Bone(head, end))

    @staticmethod
    def create_default() -> 'BodyBones':
        hips = Joint('hips', TR(glm.vec3(0, 0.85, 0)), HumanoidBone.hips)
        spine = Joint('spine',
                      TR(glm.vec3(0, 0.1, 0)), HumanoidBone.spine, parent=hips)
        chest = Joint('chest',
                      TR(glm.vec3(0, 0.1, 0)), HumanoidBone.chest, parent=spine)
        neck = Joint('neck',
                     TR(glm.vec3(0, 0.2, 0)), HumanoidBone.neck, parent=chest)
        head = Joint('head',
                     TR(glm.vec3(0, 0.1, 0)), HumanoidBone.head, parent=neck)
        head_end = Joint('head_end',
                         TR(glm.vec3(0, 0.2, 0)), HumanoidBone.endSite, parent=head)
        return BodyBones.create(hips, spine, chest, neck, head, head_end)

    def calc_world_matrix(self):
        m = glm.mat4()
        m = self.hips.calc_world_matrix(m)
        m = self.spine.calc_world_matrix(m)
        m = self.chest.calc_world_matrix(m)
        m = self.neck.calc_world_matrix(m)
        m = self.head.calc_world_matrix(m)


class LegBones(NamedTuple):
    upper: Bone
    lower: Bone
    foot: Bone
    toes: Bone

    def enumerate(self) -> Iterable[Bone]:
        yield self.upper
        yield self.lower
        yield self.foot
        yield self.toes

    @staticmethod
    def create(upper: Joint, lower: Joint, foot: Joint, toes: Joint, end: Joint) -> 'LegBones':
        return LegBones(
            Bone(upper, lower),
            Bone(lower, foot),
            Bone(foot, toes),
            Bone(toes, end)
        )

    @staticmethod
    def create_default_left(hips: Joint) -> 'LegBones':
        upper = Joint('left_upper_leg', TR(glm.vec3(0.1, 0, 0)),
                      HumanoidBone.leftUpperLeg, parent=hips)
        lower = Joint('left_lower_leg', TR(glm.vec3(0, -0.4, 0)),
                      HumanoidBone.leftLowerLeg, parent=upper)
        foot = Joint('left_foot', TR(glm.vec3(0, -0.35, 0)),
                     HumanoidBone.leftFoot, parent=lower)
        toes = Joint('left_toes', TR(glm.vec3(0, -0.1, 0.08)),
                     HumanoidBone.leftToes, parent=foot)
        end = Joint('left_toes_end', TR(glm.vec3(0, 0, 0.05)),
                    HumanoidBone.endSite, parent=toes)
        return LegBones.create(upper, lower, foot, toes, end)

    @staticmethod
    def create_default_right(hips: Joint) -> 'LegBones':
        upper = Joint('right_upper_leg', TR(glm.vec3(-0.1, 0, 0)),
                      HumanoidBone.rightUpperLeg, parent=hips)
        lower = Joint('right_lower_leg', TR(glm.vec3(0, -0.4, 0)),
                      HumanoidBone.rightLowerLeg, parent=upper)
        foot = Joint('right_foot', TR(glm.vec3(0, -0.35, 0)),
                     HumanoidBone.rightFoot, parent=lower)
        toes = Joint('right_toes', TR(glm.vec3(0, -0.1, 0.08)),
                     HumanoidBone.rightToes, parent=foot)
        end = Joint('right_toes_end', TR(glm.vec3(0, 0, 0.05)),
                    HumanoidBone.endSite, parent=toes)
        return LegBones.create(upper, lower, foot, toes, end)

    def calc_world_matrix(self, m: glm.mat4):
        m = self.upper.calc_world_matrix(m)
        m = self.lower.calc_world_matrix(m)
        m = self.foot.calc_world_matrix(m)
        m = self.toes.calc_world_matrix(m)


class FingerBones(NamedTuple):
    proximal: Bone
    intermediate: Bone
    distal: Bone

    def enumerate(self) -> Iterable[Bone]:
        yield self.proximal
        yield self.intermediate
        yield self.distal

    @staticmethod
    def create(proximal: Joint, intermediate: Joint, distal: Joint, end: Joint):
        return FingerBones(
            Bone(proximal, intermediate),
            Bone(intermediate, distal),
            Bone(distal, end))

    @staticmethod
    def create_default(prefix: str, flag: BoneFlags, hand: Joint, start: glm.vec3, dir: glm.vec3, length: float) -> 'FingerBones':
        prox = Joint(f'{prefix}_proximal',
                     TR(start), HumanoidBone.baseflag(BoneBase.finger_1, flag), parent=hand)
        inter = Joint(f'{prefix}_intermediate',
                      TR(dir*length), HumanoidBone.baseflag(BoneBase.finger_2, flag), parent=prox)
        distal = Joint(f'{prefix}_distal',
                       TR(dir*length*0.8), HumanoidBone.baseflag(BoneBase.finger_3, flag), parent=inter)
        end = Joint(f'{prefix}_end',
                    TR(dir*length*0.8*0.8), HumanoidBone.endSite, parent=distal)
        return FingerBones.create(prox, inter, distal, end)

    def calc_world_matrix(self, m: glm.mat4):
        m = self.proximal.calc_world_matrix(m)
        m = self.intermediate.calc_world_matrix(m)
        m = self.distal.calc_world_matrix(m)


class ArmBones(NamedTuple):
    shoulder: Bone
    upper: Bone
    lower: Bone
    hand: Bone
    thumb: Optional[FingerBones] = None
    index: Optional[FingerBones] = None
    middle: Optional[FingerBones] = None
    ring: Optional[FingerBones] = None
    little: Optional[FingerBones] = None

    def enumerate(self) -> Iterable[Bone]:
        yield self.shoulder
        yield self.upper
        yield self.lower
        yield self.hand
        if self.thumb:
            yield from self.thumb.enumerate()
        if self.index:
            yield from self.index.enumerate()
        if self.middle:
            yield from self.middle.enumerate()
        if self.ring:
            yield from self.ring.enumerate()
        if self.little:
            yield from self.little.enumerate()

    @staticmethod
    def create(shoulder: Joint, upper: Joint, lower: Joint, hand: Joint, *,
               middle: Union[Joint, FingerBones],
               thumb: Optional[FingerBones] = None,
               index: Optional[FingerBones] = None,
               ring: Optional[FingerBones] = None,
               little: Optional[FingerBones] = None
               ) -> 'ArmBones':
        if isinstance(middle, FingerBones):
            return ArmBones(
                Bone(shoulder, upper),
                Bone(upper, lower),
                Bone(lower, hand),
                Bone(hand, middle.proximal.head),
                thumb=thumb,
                index=index,
                middle=middle,
                ring=ring,
                little=little
            )
        else:
            return ArmBones(
                Bone(shoulder, upper),
                Bone(upper, lower),
                Bone(lower, hand),
                Bone(hand, middle),
                middle=None,
            )

    @staticmethod
    def create_default_left(chest: Joint):
        shoulder = Joint('left_shoulder', TR(glm.vec3(0.1, 0.2, 0)),
                         HumanoidBone.leftShoulder, parent=chest)
        upper = Joint('left_upper_arm', TR(glm.vec3(0.05, 0, 0)),
                      HumanoidBone.leftUpperArm, parent=shoulder)
        lower = Joint('left_lower_arm', TR(glm.vec3(0.2, 0, 0)),
                      HumanoidBone.leftLowerArm, parent=upper)
        hand = Joint('left_hand', TR(glm.vec3(0.2, 0, 0)),
                     HumanoidBone.leftHand, parent=lower)
        left = glm.vec3(1, 0, 0)
        thumb = FingerBones.create_default('left', BoneFlags.Left | BoneFlags.FingerThumbnail, hand,
                                           glm.vec3(0.03, -0.01, 0.02), left, 0.03)
        index = FingerBones.create_default('left', BoneFlags.Left | BoneFlags.FingerIndex, hand,
                                           glm.vec3(0.075, 0, 0.015), left, 0.03)
        middle = FingerBones.create_default('left', BoneFlags.Left | BoneFlags.FingerMiddle, hand,
                                            glm.vec3(0.08, 0, 0), left, 0.03)
        ring = FingerBones.create_default('left', BoneFlags.Left | BoneFlags.FingerRing, hand,
                                          glm.vec3(0.075, 0, -0.015), left, 0.03)
        little = FingerBones.create_default('left', BoneFlags.Left | BoneFlags.FingerLittle, hand,
                                            glm.vec3(0.07, 0, -0.03), left, 0.03)

        return ArmBones.create(shoulder, upper, lower, hand,
                               thumb=thumb,
                               index=index,
                               middle=middle,
                               ring=ring,
                               little=little
                               )

    @staticmethod
    def create_default_right(chest: Joint):
        shoulder = Joint('right_shoulder', TR(glm.vec3(-0.1, 0.2, 0)),
                         HumanoidBone.rightShoulder, parent=chest)
        upper = Joint('right_upper_arm', TR(glm.vec3(-0.05, 0, 0)),
                      HumanoidBone.rightUpperArm, parent=shoulder)
        lower = Joint('right_lower_arm', TR(glm.vec3(-0.2, 0, 0)),
                      HumanoidBone.rightLowerArm, parent=upper)
        hand = Joint('right_hand', TR(glm.vec3(-0.2, 0, 0)),
                     HumanoidBone.rightHand, parent=lower)
        right = glm.vec3(-1, 0, 0)
        thumb = FingerBones.create_default('right', BoneFlags.Right | BoneFlags.FingerThumbnail, hand,
                                           glm.vec3(-0.03, -0.01, 0.02), right, 0.03)
        index = FingerBones.create_default('right', BoneFlags.Right | BoneFlags.FingerIndex, hand,
                                           glm.vec3(-0.075, 0, 0.015), right, 0.03)
        middle = FingerBones.create_default('right', BoneFlags.Right | BoneFlags.FingerMiddle, hand,
                                            glm.vec3(-0.08, 0, 0), right, 0.03)
        ring = FingerBones.create_default('right', BoneFlags.Right | BoneFlags.FingerRing, hand,
                                          glm.vec3(-0.075, 0, -0.015), right, 0.03)
        little = FingerBones.create_default('right', BoneFlags.Right | BoneFlags.FingerLittle, hand,
                                            glm.vec3(-0.07, 0, -0.03), right, 0.03)

        return ArmBones.create(shoulder, upper, lower, hand,
                               thumb=thumb,
                               index=index,
                               middle=middle,
                               ring=ring,
                               little=little
                               )

    def calc_world_matrix(self, m: glm.mat4):
        m = self.shoulder.calc_world_matrix(m)
        m = self.upper.calc_world_matrix(m)
        m = self.lower.calc_world_matrix(m)
        m = self.hand.calc_world_matrix(m)
        if self.thumb:
            f = m
            for bone in self.thumb.enumerate():
                f = bone.calc_world_matrix(f)
        if self.index:
            f = m
            for bone in self.index.enumerate():
                f = bone.calc_world_matrix(f)
        if self.middle:
            f = m
            for bone in self.middle.enumerate():
                f = bone.calc_world_matrix(f)
        if self.ring:
            f = m
            for bone in self.ring.enumerate():
                f = bone.calc_world_matrix(f)
        if self.little:
            f = m
            for bone in self.little.enumerate():
                f = bone.calc_world_matrix(f)

    def strict_tpose(self, m: glm.mat4):
        m = self.shoulder.strict_tpose(m)
        m = self.upper.strict_tpose(m)
        m = self.lower.strict_tpose(m)
        m = self.hand.strict_tpose(m)
        if self.thumb:
            f = m
            for bone in self.thumb.enumerate():
                f = bone.strict_tpose(f)
        if self.index:
            f = m
            for bone in self.index.enumerate():
                f = bone.strict_tpose(f)
        if self.middle:
            f = m
            for bone in self.middle.enumerate():
                f = bone.strict_tpose(f)
        if self.ring:
            f = m
            for bone in self.ring.enumerate():
                f = bone.strict_tpose(f)
        if self.little:
            f = m
            for bone in self.little.enumerate():
                f = bone.strict_tpose(f)


class Skeleton:
    def __init__(self, body: BodyBones,
                 left_leg: Optional[LegBones] = None, right_leg: Optional[LegBones] = None,
                 left_arm: Optional[ArmBones] = None, right_arm: Optional[ArmBones] = None) -> None:
        self.body = body
        self.left_leg = left_leg
        self.right_leg = right_leg
        self.left_arm = left_arm
        self.right_arm = right_arm

    @staticmethod
    def create_default():
        body = BodyBones.create_default()
        left_leg = LegBones.create_default_left(body.hips.head)
        right_leg = LegBones.create_default_right(body.hips.head)
        left_arm = ArmBones.create_default_left(body.chest.head)
        right_arm = ArmBones.create_default_right(body.chest.head)
        return Skeleton(body,
                        left_leg=left_leg, right_leg=right_leg,
                        left_arm=left_arm, right_arm=right_arm)

    def calc_world_matrix(self):
        self.body.calc_world_matrix()
        if self.left_arm:
            self.left_arm.calc_world_matrix(
                self.body.chest.head.world.get_matrix())
        if self.right_arm:
            self.right_arm.calc_world_matrix(
                self.body.chest.head.world.get_matrix())
        if self.left_leg:
            self.left_leg.calc_world_matrix(
                self.body.hips.head.world.get_matrix())
        if self.right_leg:
            self.right_leg.calc_world_matrix(
                self.body.hips.head.world.get_matrix())

    def strict_tpose(self):
        m = glm.mat4()
        for bone in self.body.enumerate():
            m = bone.strict_tpose(m)
        if self.left_leg:
            m = self.body.hips.head.world.get_matrix()
            for bone in self.left_leg.enumerate():
                m = bone.strict_tpose(m)
        if self.right_leg:
            m = self.body.hips.head.world.get_matrix()
            for bone in self.right_leg.enumerate():
                m = bone.strict_tpose(m)
        if self.left_arm:
            m = self.body.chest.head.world.get_matrix()
            self.left_arm.strict_tpose(m)
        if self.right_arm:
            m = self.body.chest.head.world.get_matrix()
            self.right_arm.strict_tpose(m)

    def enumerate(self) -> Iterable[Bone]:
        yield from self.body.enumerate()
        if self.left_arm:
            yield from self.left_arm.enumerate()
        if self.right_arm:
            yield from self.right_arm.enumerate()
        if self.left_leg:
            yield from self.left_leg.enumerate()
        if self.right_leg:
            yield from self.right_leg.enumerate()

    def clear_pose(self):
        for bone in self.enumerate():
            bone.head.pose = glm.quat()
        self.calc_world_matrix()

    def cancel_axis(self):
        self.calc_world_matrix()
        for bone in self.enumerate():
            bone.cancel_axis()

    def clear_axis(self):
        for bone in self.enumerate():
            bone.clear_axis()
        self.calc_world_matrix()

    def to_pose(self) -> Pose:
        pose = Pose('pose')
        for bone in self.enumerate():
            pose.bones.append(BonePose(bone.head.name, bone.head.humanoid_bone,
                                       Transform.from_rotation(bone.head.pose)))
        return pose
