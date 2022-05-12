from typing import Iterable
import glm
from pydear.gizmo.shapes.shape import Shape
from pydear.gizmo.primitive import Quad
from ..scene.node import Node
from ..humanoid.humanoid_skeleton import HumanoidSkeleton, Fingers, HumanoidBone


class BoneShape(Shape):
    '''
    Z
    0    3
    +----+
    |    |
    +----+
    1    2X
    '''

    def __init__(self, width: float, height: float, depth: float, *, matrix: glm.mat4, color: glm.vec3) -> None:
        super().__init__(matrix, False)
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
        v0 = glm.vec3(-x, 0, z)
        v1 = glm.vec3(-x, 0, -z)
        v2 = glm.vec3(x, 0, -z)
        v3 = glm.vec3(x, 0, z)
        v4 = glm.vec3(-x, y, z)
        v5 = glm.vec3(-x, y, -z)
        v6 = glm.vec3(x, y, -z)
        v7 = glm.vec3(x, y, z)
        self.quads = [
            Quad.from_points(v0, v1, v2, v3),
            Quad.from_points(v3, v2, v6, v7),
            Quad.from_points(v7, v6, v5, v4),
            Quad.from_points(v4, v5, v1, v0),
            Quad.from_points(v4, v0, v3, v7),
            Quad.from_points(v1, v5, v6, v2),
        ]

    @staticmethod
    def from_node(node: Node) -> 'BoneShape':
        assert node.humanoid_bone
        assert node.humanoid_tail

        color = glm.vec3(1, 1, 1)
        width = 0.005
        height = 0.001
        if node.humanoid_bone.get_classification().finger != Fingers.NotFinger:
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
                up = glm.vec3(0, 0, 1)
            else:
                up = glm.vec3(0, 1, 0)
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
                    width = 0.01
                    height = 0.002
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

        return BoneShape(width, height, length, color=color, matrix=matrix)

    def get_color(self) -> glm.vec4:
        return self.color

    def get_quads(self) -> Iterable[Quad]:
        return self.quads
