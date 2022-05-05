from enum import Enum, auto
import glm
from .bvh_node import Node
from ..humanoid_bones import HumanoidBone


class Unit(Enum):
    Unknown = auto()
    CentiMeter = auto()
    TenCentiMeter = auto()

    def to_meter(self):
        match self:
            case Unit.TenCentiMeter:
                return 1/10
            case Unit.CentiMeter:
                return 1/100
            case Unit.Unknown:
                return 1


class SkeletonChecker:
    def __init__(self, root: Node):
        self.hips_y = 0
        self.min_y = 0
        self.forward = 'UNKNOWN'
        self.traverse(root)
        self.hips_height = self.hips_y - self.min_y

    def traverse(self, node: Node, parent=glm.vec3(0)):
        current = parent + node.offset
        if node.humanoid_bone == HumanoidBone.hips:
            self.hips_y = current.y
        elif node.humanoid_bone == HumanoidBone.leftUpperLeg:
            if current.x > 0:
                self.forward = 'Z_POSITIVE'
            elif current.x < 0:
                self.forward = 'Z_NEGATIVE'
            else:
                self.forward = 'UNKNOWN?'
        if current.y < self.min_y:
            self.min_y = current.y
        for child in node.children:
            self.traverse(child, current)

    def get_unit(self) -> Unit:
        # self.scale = 1
        if self.hips_height > 70 and self.hips_height < 100:
            # cm to meter
            # self.scale = 0.01
            return Unit.CentiMeter
        elif self.hips_height > 7 and self.hips_height < 10:
            # 10cm to meter ?
            # self.scale = 0.1
            return Unit.TenCentiMeter

        return Unit.Unknown
