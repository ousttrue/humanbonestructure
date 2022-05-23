from typing import Iterable, Dict, Tuple, TypedDict, Callable, Optional, TypeAlias, Union, NamedTuple
from enum import Enum, auto
import glm
from pydear.gizmo.shapes.shape import Shape
from pydear.gizmo.primitive import Quad
from pydear.gizmo.gizmo import Gizmo
from ..humanoid.humanoid_bones import HumanoidBone
from ..humanoid.bone import Skeleton, Bone, AxisPositiveNegative
from ..humanoid.coordinate import Coordinate
from .node import Node

UP_COLOR = glm.vec4(0.8, 0.2, 0.2, 1)


GetCoords: TypeAlias = Callable[[HumanoidBone], Coordinate]


BLENDER_COORDS = Coordinate(
    yaw=glm.vec3(0, 0, 1),
    pitch=glm.vec3(1, 0, 0),
    roll=glm.vec3(0, 1, 0))


class BoneShapeSetting(NamedTuple):
    width: float
    height: float
    color: glm.vec3
    line_size: float

    @staticmethod
    def from_humanoid_bone(humanoid_bone: HumanoidBone) -> 'BoneShapeSetting':
        color = glm.vec3(1, 1, 1)
        width = float('nan')
        height = float('nan')
        line_size = 0.1
        if humanoid_bone.is_finger():
            width = 0.006
            height = 0.004
            line_size = 0.02
            if 'Index' in humanoid_bone.name or 'Ring' in humanoid_bone.name:
                if humanoid_bone.name.endswith("Intermediate"):
                    color = glm.vec3(0.1, 0.4, 0.8)
                else:
                    color = glm.vec3(0.2, 0.7, 0.9)
            else:
                if humanoid_bone.name.endswith("Intermediate"):
                    color = glm.vec3(0.8, 0.4, 0.1)
                else:
                    color = glm.vec3(0.9, 0.7, 0.2)
            if 'Thumb' in humanoid_bone.name:
                pass
            else:
                pass
        else:
            match humanoid_bone:
                case (
                    HumanoidBone.leftShoulder |
                    HumanoidBone.leftUpperArm | HumanoidBone.leftLowerArm |
                    HumanoidBone.leftUpperArm | HumanoidBone.leftLowerArm |
                    HumanoidBone.rightShoulder |
                    HumanoidBone.rightUpperArm | HumanoidBone.rightLowerArm |
                    HumanoidBone.rightUpperArm | HumanoidBone.rightLowerArm
                ):
                    color = glm.vec3(0.3, 0.6, 0.1) if 'Lower' in humanoid_bone.name else glm.vec3(
                        0.7, 0.9, 0.2)
                    width = 0.02
                    height = 0.01
                case (HumanoidBone.leftHand | HumanoidBone.leftHand |
                        HumanoidBone.rightHand | HumanoidBone.rightHand
                      ):
                    color = glm.vec3(0.8, 0.8, 0.8)
                    width = 0.02
                    height = 0.005
                case (HumanoidBone.head):
                    color = glm.vec3(0.8, 0.8, 0.2)
                    width = 0.06
                    height = 0.06
                case (HumanoidBone.neck):
                    color = glm.vec3(0.4, 0.4, 0.2)
                    width = 0.02
                    height = 0.02
                case (HumanoidBone.chest | HumanoidBone.hips):
                    color = glm.vec3(0.8, 0.8, 0.2)
                    width = 0.05
                    height = 0.04
                case (HumanoidBone.spine):
                    color = glm.vec3(0.4, 0.4, 0.2)
                    width = 0.04
                    height = 0.03
                case (HumanoidBone.leftUpperLeg | HumanoidBone.leftLowerLeg | HumanoidBone.leftFoot | HumanoidBone.leftToes |
                        HumanoidBone.rightUpperLeg | HumanoidBone.rightLowerLeg | HumanoidBone.rightFoot | HumanoidBone.rightToes):
                    color = glm.vec3(0.3, 0.6, 0.1)
                    if humanoid_bone in (HumanoidBone.leftUpperLeg, HumanoidBone.leftFoot, HumanoidBone.rightUpperLeg, HumanoidBone.rightFoot):
                        color = glm.vec3(0.7, 0.9, 0.2)
                    width = 0.03
                    height = 0.02
        return BoneShapeSetting(width, height, color, line_size)


class BoneShape(Shape):
    '''
    Z
    0    3
    +----+
    |    |
    +----+
    1    2X
    '''

    def __init__(self, matrix: glm.mat4, width: float, height: float, tail: glm.vec3, up_dir: glm.vec3,
                 color: glm.vec3, line_size=0.1) -> None:
        super().__init__(matrix)
        if isinstance(color, glm.vec4):
            self.color = color
        elif isinstance(color, glm.vec3):
            self.color = glm.vec4(color, 1)
        else:
            self.color = glm.vec4(1, 1, 1, 1)
        self.width = width
        self.height = height
        # self.depth = depth
        x = self.width
        # y = self.depth
        z = self.height

        assert up_dir
        head_tail = tail
        z_axis = glm.normalize(head_tail)
        x_axis = glm.normalize(glm.cross(up_dir, z_axis))
        y_axis = glm.normalize(glm.cross(z_axis, x_axis))
        # y_axis = up_dir
        height = glm.vec3()

        v0 = x_axis*x+y_axis*z
        v1 = x_axis*x-y_axis*z
        v2 = -x_axis*x-y_axis*z
        v3 = -x_axis*x+y_axis*z
        v4 = head_tail + x_axis*x+y_axis*z
        v5 = head_tail + x_axis*x-y_axis*z
        v6 = head_tail - x_axis*x-y_axis*z
        v7 = head_tail - x_axis*x+y_axis*z
        a = glm.quat()
        self.lines = [
            (a*glm.vec3(0, 0, 0), a *
                glm.vec3(line_size, 0, 0), glm.vec4(1, 0, 0, 1)),
            (a*glm.vec3(0, 0, 0), a*glm.vec3(0,
                                             line_size, 0), glm.vec4(0, 1, 0, 1)),
            (a*glm.vec3(0, 0, 0), a*glm.vec3(0,
                                             0, line_size), glm.vec4(0, 0, 1, 1)),
        ]

        self.quads = [
            Quad.from_points(v0, v1, v2, v3),  # back
            Quad.from_points(v3, v2, v6, v7),  # right
            Quad.from_points(v7, v6, v5, v4),  # forward
            Quad.from_points(v4, v5, v1, v0),  # left
            Quad.from_points(v4, v0, v3, v7),  # top(red)
            Quad.from_points(v1, v5, v6, v2),  # bottom
        ]

    @staticmethod
    def from_node(node: Node) -> 'BoneShape':
        assert node.humanoid_bone
        assert node.humanoid_tail
        setting = BoneShapeSetting.from_humanoid_bone(node.humanoid_bone)
        m = node.world_matrix * glm.mat4(node.local_axis)
        tail = glm.inverse(m) * node.humanoid_tail.world_matrix[3].xyz
        up_dir = glm.inverse(m) * node.humanoid_bone.world_second
        return BoneShape(m, setting.width, setting.height, tail, up_dir, color=setting.color, line_size=setting.line_size)

    @staticmethod
    def from_root(root: Node, gizmo: Gizmo, *,
                  get_coordinate: Optional[GetCoords] = None) -> Dict[Node, Shape]:
        node_shape_map: Dict[Node, Shape] = {}
        for bone in HumanoidBone:
            if bone.is_enable():
                node = root.find_humanoid_bone(bone)
                if node:
                    shape = BoneShape.from_node(node)
                    gizmo.add_shape(shape)
                    node_shape_map[node] = shape
        return node_shape_map

    @staticmethod
    def from_bone(bone: Bone) -> 'BoneShape':
        setting = BoneShapeSetting.from_humanoid_bone(
            bone.head.humanoid_bone)
        tail = bone.get_local_tail()
        return BoneShape(bone.head.world.get_matrix() * glm.mat4(bone.local_axis), setting.width, setting.height, tail,
                         color=setting.color,
                         line_size=setting.line_size,
                         up_dir=bone.get_up_dir())

    @staticmethod
    def from_skeleton(skeleton: Skeleton, gizmo: Gizmo) -> Dict[Bone, Shape]:
        bone_shape_map: Dict[Bone, Shape] = {}
        bones = [
            skeleton.body.hips,
            skeleton.body.spine,
            skeleton.body.chest,
            skeleton.body.neck,
            skeleton.body.head,
        ]
        if skeleton.left_leg:
            bones += [
                skeleton.left_leg.upper,
                skeleton.left_leg.lower,
                skeleton.left_leg.foot,
                skeleton.left_leg.toes,
            ]
        if skeleton.right_leg:
            bones += [
                skeleton.right_leg.upper,
                skeleton.right_leg.lower,
                skeleton.right_leg.foot,
                skeleton.right_leg.toes,
            ]
        if skeleton.left_arm:
            bones += [
                skeleton.left_arm.shoulder,
                skeleton.left_arm.upper,
                skeleton.left_arm.lower,
                skeleton.left_arm.hand,
            ]
            if skeleton.left_arm.thumb:
                bones += [
                    skeleton.left_arm.thumb.proximal,
                    skeleton.left_arm.thumb.intermediate,
                    skeleton.left_arm.thumb.distal,
                ]
            if skeleton.left_arm.index:
                bones += [
                    skeleton.left_arm.index.proximal,
                    skeleton.left_arm.index.intermediate,
                    skeleton.left_arm.index.distal,
                ]
            if skeleton.left_arm.middle:
                bones += [
                    skeleton.left_arm.middle.proximal,
                    skeleton.left_arm.middle.intermediate,
                    skeleton.left_arm.middle.distal,
                ]
            if skeleton.left_arm.ring:
                bones += [
                    skeleton.left_arm.ring.proximal,
                    skeleton.left_arm.ring.intermediate,
                    skeleton.left_arm.ring.distal,
                ]
            if skeleton.left_arm.little:
                bones += [
                    skeleton.left_arm.little.proximal,
                    skeleton.left_arm.little.intermediate,
                    skeleton.left_arm.little.distal,
                ]
        #
        if skeleton.right_arm:
            bones += [
                skeleton.right_arm.shoulder,
                skeleton.right_arm.upper,
                skeleton.right_arm.lower,
                skeleton.right_arm.hand,
            ]
            if skeleton.right_arm.thumb:
                bones += [
                    skeleton.right_arm.thumb.proximal,
                    skeleton.right_arm.thumb.intermediate,
                    skeleton.right_arm.thumb.distal,
                ]
            if skeleton.right_arm.index:
                bones += [
                    skeleton.right_arm.index.proximal,
                    skeleton.right_arm.index.intermediate,
                    skeleton.right_arm.index.distal,
                ]
            if skeleton.right_arm.middle:
                bones += [
                    skeleton.right_arm.middle.proximal,
                    skeleton.right_arm.middle.intermediate,
                    skeleton.right_arm.middle.distal,
                ]
            if skeleton.right_arm.ring:
                bones += [
                    skeleton.right_arm.ring.proximal,
                    skeleton.right_arm.ring.intermediate,
                    skeleton.right_arm.ring.distal,
                ]
            if skeleton.right_arm.little:
                bones += [
                    skeleton.right_arm.little.proximal,
                    skeleton.right_arm.little.intermediate,
                    skeleton.right_arm.little.distal,
                ]
        for bone in bones:
            shape = BoneShape.from_bone(bone)
            gizmo.add_shape(shape)
            bone_shape_map[bone] = shape
        return bone_shape_map

    def get_quads(self) -> Iterable[Tuple[Quad, glm.vec4]]:
        for i, quad in enumerate(self.quads):
            yield quad, self.color if i != 4 else UP_COLOR

    def get_lines(self) -> Iterable[Tuple[glm.vec3, glm.vec3, glm.vec4]]:
        return self.lines
