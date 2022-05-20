from typing import Iterable, Dict, Tuple, TypedDict, Callable, Optional, TypeAlias, Union, NamedTuple
from enum import Enum, auto
import glm
from pydear.gizmo.shapes.shape import Shape
from pydear.gizmo.primitive import Quad
from pydear.gizmo.gizmo import Gizmo
from ..humanoid.humanoid_bones import HumanoidBone
from ..humanoid.bone import Skeleton, Bone, HeadTailAxis
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

    def __init__(self, width: float, height: float, depth: Union[float, Tuple[glm.vec3, glm.vec3]], *, matrix: glm.mat4, color: glm.vec3, coordinate=None, up_dir=None, local_axis=None, line_size=0.1) -> None:
        super().__init__(matrix)
        if isinstance(color, glm.vec4):
            self.color = color
        elif isinstance(color, glm.vec3):
            self.color = glm.vec4(color, 1)
        else:
            self.color = glm.vec4(1, 1, 1, 1)
        self.width = width
        self.height = height
        self.depth = depth
        x = self.width
        y = self.depth
        z = self.height

        match depth:
            case float():
                assert coordinate
                yaw = coordinate['yaw']
                pitch = coordinate['pitch']
                roll = coordinate['roll']
                v0 = -pitch*x+yaw*z
                v1 = -pitch*x-yaw*z
                v2 = pitch*x-yaw*z
                v3 = pitch*x+yaw*z
                v4 = -pitch*x+roll*y+yaw*z
                v5 = -pitch*x+roll*y-yaw*z
                v6 = pitch*x+roll*y-yaw*z
                v7 = pitch*x+roll*y+yaw*z
                self.lines = [
                    (glm.vec3(0, 0, 0), glm.vec3(
                        line_size, 0, 0), glm.vec4(1, 0, 0, 1)),
                    (glm.vec3(0, 0, 0), glm.vec3(
                        0, line_size, 0), glm.vec4(0, 1, 0, 1)),
                    (glm.vec3(0, 0, 0), glm.vec3(
                        0, 0, line_size), glm.vec4(0, 0, 1, 1)),
                ]
            case (head, tail):
                assert up_dir
                head_tail = tail - head
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
                a = local_axis
                self.lines = [
                    (a*glm.vec3(0, 0, 0), a *
                     glm.vec3(line_size, 0, 0), glm.vec4(1, 0, 0, 1)),
                    (a*glm.vec3(0, 0, 0), a*glm.vec3(0,
                     line_size, 0), glm.vec4(0, 1, 0, 1)),
                    (a*glm.vec3(0, 0, 0), a*glm.vec3(0,
                     0, line_size), glm.vec4(0, 0, 1, 1)),
                ]
            case _:
                raise RuntimeError()
        self.quads = [
            Quad.from_points(v0, v1, v2, v3),  # back
            Quad.from_points(v3, v2, v6, v7),  # right
            Quad.from_points(v7, v6, v5, v4),  # forward
            Quad.from_points(v4, v5, v1, v0),  # left
            Quad.from_points(v4, v0, v3, v7),  # top(red)
            Quad.from_points(v1, v5, v6, v2),  # bottom
        ]

    @staticmethod
    def from_node(node: Node, *, get_coordinate: Optional[GetCoords] = None) -> 'BoneShape':
        assert node.humanoid_bone
        assert node.humanoid_tail

        setting = BoneShapeSetting.from_humanoid_bone(node.humanoid_bone)

        matrix = node.world_matrix * glm.mat4(node.local_axis)

        # bone
        length = glm.length(
            node.world_matrix[3].xyz - node.humanoid_tail.world_matrix[3].xyz)

        if get_coordinate:
            coordinate = get_coordinate(node.humanoid_bone)
            return BoneShape(setting.width, setting.height, length, color=setting.color, matrix=matrix, coordinate=coordinate, line_size=setting.line_size)
        else:
            # head tail
            assert node.humanoid_tail
            head = node.world_matrix[3].xyz
            tail = node.humanoid_tail.world_matrix[3].xyz
            return BoneShape(setting.width, setting.height, (head, tail), color=setting.color, matrix=matrix, line_size=setting.line_size, up_dir=node.humanoid_bone.world_second, local_axis=node.local_axis)

    @staticmethod
    def from_root(root: Node, gizmo: Gizmo, *,
                  get_coordinate: Optional[GetCoords] = None) -> Dict[Node, Shape]:
        node_shape_map: Dict[Node, Shape] = {}
        for bone in HumanoidBone:
            if bone.is_enable():
                node = root.find_humanoid_bone(bone)
                if node:
                    shape = BoneShape.from_node(
                        node, get_coordinate=get_coordinate)
                    gizmo.add_shape(shape)
                    node_shape_map[node] = shape
        return node_shape_map

    @staticmethod
    def from_bone(bone: Bone) -> 'BoneShape':
        setting = BoneShapeSetting.from_humanoid_bone(
            bone.head.humanoid_bone)
        match bone.head_tail_axis:
            case (HeadTailAxis.XPositive | HeadTailAxis.XNegative |
                  HeadTailAxis.YPositive | HeadTailAxis.YNegative |
                  HeadTailAxis.ZPositive | HeadTailAxis.ZNegative):
                return BoneShape(setting.width, setting.height, bone.get_length(),
                                 color=setting.color, matrix=bone.head.world.get_matrix(),
                                 coordinate=bone.get_coordinate(), line_size=setting.line_size)
            case HeadTailAxis.Other:
                # fallback head tail
                # assert node.humanoid_tail
                head = bone.head.world.get_matrix()[3].xyz
                tail = bone.tail.world.get_matrix()[3].xyz
                return BoneShape(setting.width, setting.height, (head, tail),
                                 color=setting.color,
                                 matrix=glm.translate(
                                     bone.head.world.translation),
                                 line_size=setting.line_size,
                                 up_dir=bone.head.humanoid_bone.world_second, local_axis=bone.head.world.rotation)
            case _:
                raise RuntimeError()

    @staticmethod
    def from_skeleton(skeleton: Skeleton, gizmo: Gizmo):
        for shape in (
            BoneShape.from_bone(skeleton.body.hips),
            BoneShape.from_bone(skeleton.body.spine),
            BoneShape.from_bone(skeleton.body.chest),
            BoneShape.from_bone(skeleton.body.neck),
            BoneShape.from_bone(skeleton.body.head),

            BoneShape.from_bone(skeleton.left_leg.upper),
            BoneShape.from_bone(skeleton.left_leg.lower),
            BoneShape.from_bone(skeleton.left_leg.foot),

            BoneShape.from_bone(skeleton.right_leg.upper),
            BoneShape.from_bone(skeleton.right_leg.lower),
            BoneShape.from_bone(skeleton.right_leg.foot),
        ):
            gizmo.add_shape(shape)

    def get_quads(self) -> Iterable[Tuple[Quad, glm.vec4]]:
        for i, quad in enumerate(self.quads):
            yield quad, self.color if i != 4 else UP_COLOR

    def get_lines(self) -> Iterable[Tuple[glm.vec3, glm.vec3, glm.vec4]]:
        return self.lines
