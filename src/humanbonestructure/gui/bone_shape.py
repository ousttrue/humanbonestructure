from typing import Iterable, Dict, Tuple, TypedDict
from enum import Enum, auto
import glm
from pydear.gizmo.shapes.shape import Shape
from pydear.gizmo.primitive import Quad
from pydear.gizmo.gizmo import Gizmo
from ..scene.node import Node
from ..humanoid.humanoid_bones import HumanoidBone

UP_COLOR = glm.vec4(0.8, 0.2, 0.2, 1)


class Coordinate(TypedDict):
    yaw: glm.vec3
    pitch: glm.vec3
    roll: glm.vec3


BLENDER_COORDS = Coordinate(
    yaw=glm.vec3(0, 0, 1),
    pitch=glm.vec3(1, 0, 0),
    roll=glm.vec3(0, 1, 0))


class BoneShape(Shape):
    '''
    Z
    0    3
    +----+
    |    |
    +----+
    1    2X
    '''

    def __init__(self, width: float, height: float, depth: float, *, matrix: glm.mat4, color: glm.vec3, coordinate=BLENDER_COORDS, line_size=0.1) -> None:
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
        self.quads = [
            Quad.from_points(v0, v1, v2, v3),  # back
            Quad.from_points(v3, v2, v6, v7),  # right
            Quad.from_points(v7, v6, v5, v4),  # forward
            Quad.from_points(v4, v5, v1, v0),  # left
            Quad.from_points(v4, v0, v3, v7),  # top
            Quad.from_points(v1, v5, v6, v2),  # bottom
        ]
        self.lines = [
            (glm.vec3(0, 0, 0), glm.vec3(line_size, 0, 0), glm.vec4(1, 0, 0, 1)),
            (glm.vec3(0, 0, 0), glm.vec3(0, line_size, 0), glm.vec4(0, 1, 0, 1)),
            (glm.vec3(0, 0, 0), glm.vec3(0, 0, line_size), glm.vec4(0, 0, 1, 1)),
        ]

    @staticmethod
    def from_node(node: Node, *, coordinate=BLENDER_COORDS) -> 'BoneShape':
        assert node.humanoid_bone
        assert node.humanoid_tail

        color = glm.vec3(1, 1, 1)
        width = float('nan')
        height = float('nan')
        line_size = 0.1
        if node.humanoid_bone.is_finger():
            width = 0.006
            height = 0.004
            line_size = 0.02
            if 'Index' in node.humanoid_bone.name or 'Ring' in node.humanoid_bone.name:
                if node.humanoid_bone.name.endswith("Intermediate"):
                    color = glm.vec3(0.1, 0.4, 0.8)
                else:
                    color = glm.vec3(0.2, 0.7, 0.9)
            else:
                if node.humanoid_bone.name.endswith("Intermediate"):
                    color = glm.vec3(0.8, 0.4, 0.1)
                else:
                    color = glm.vec3(0.9, 0.7, 0.2)
            if 'Thumb' in node.humanoid_bone.name:
                pass
            else:
                pass
        else:
            match node.humanoid_bone:
                case (
                    HumanoidBone.leftShoulder |
                    HumanoidBone.leftUpperArm | HumanoidBone.leftLowerArm |
                    HumanoidBone.leftUpperArm | HumanoidBone.leftLowerArm |
                    HumanoidBone.rightShoulder |
                    HumanoidBone.rightUpperArm | HumanoidBone.rightLowerArm |
                    HumanoidBone.rightUpperArm | HumanoidBone.rightLowerArm
                ):
                    color = glm.vec3(0.3, 0.6, 0.1) if 'Lower' in node.humanoid_bone.name else glm.vec3(
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
                    if node.humanoid_bone in (HumanoidBone.leftUpperLeg, HumanoidBone.leftFoot, HumanoidBone.rightUpperLeg, HumanoidBone.rightFoot):
                        color = glm.vec3(0.7, 0.9, 0.2)
                    width = 0.03
                    height = 0.02

        matrix = node.world_matrix * glm.mat4(node.local_axis)

        # bone
        length = glm.length(
            node.world_matrix[3].xyz - node.humanoid_tail.world_matrix[3].xyz)

        return BoneShape(width, height, length, color=color, matrix=matrix, coordinate=coordinate, line_size=line_size)

    @staticmethod
    def from_root(root: Node, gizmo: Gizmo, *, coordinate=BLENDER_COORDS) -> Dict[Node, Shape]:
        node_shape_map: Dict[Node, Shape] = {}
        for bone in HumanoidBone:
            if bone.is_enable():
                node = root.find_humanoid_bone(bone)
                if node:
                    shape = BoneShape.from_node(node, coordinate=coordinate)
                    gizmo.add_shape(shape)
                    node_shape_map[node] = shape
        return node_shape_map

    def get_quads(self) -> Iterable[Tuple[Quad, glm.vec4]]:
        for i, quad in enumerate(self.quads):
            yield quad, self.color if i != 4 else UP_COLOR

    def get_lines(self) -> Iterable[Tuple[glm.vec3, glm.vec3, glm.vec4]]:
        return self.lines
