from typing import Optional
from OpenGL import GL
import logging
import glm
from pydear.scene.camera import Camera
from pydear.gizmo.gizmo import Gizmo
from ..humanoid.humanoid_skeleton import HumanoidSkeleton, Fingers, HumanoidBone
from ..scene.node import Node

LOGGER = logging.getLogger(__name__)
RED = glm.vec4(1, 0, 0, 1)
GREEN = glm.vec4(0, 1, 0, 1)
BLUE = glm.vec4(0, 0, 1, 1)
SELECTED_COLOR = glm.vec3(0.5, 0.5, 1)


class PoseScene:
    def __init__(self) -> None:
        self.skeleton = None
        self.root: Optional[Node] = None
        self.selected = None
        #
        self.gizmo = Gizmo()

    def set_skeleton(self, skeleton: Optional[HumanoidSkeleton]):
        self.skeleton = skeleton
        if self.skeleton:
            self.root = self.skeleton.to_node()
            self.root.init_human_bones()
            self.root.calc_world_matrix(glm.mat4())
            for bone, _ in self.root.traverse_node_and_parent():
                if bone.humanoid_bone.is_enable():
                    bone.local_axis = glm.quat(
                        bone.humanoid_bone.get_classification().get_local_axis())
        else:
            self.root = None

    def get_root(self) -> Optional[Node]:
        return self.root

    def get_selected(self):
        return self.selected

    def set_selected(self, selected):
        self.selected = selected

    def show_option(self):
        pass

    def render(self, camera: Camera):
        GL.glEnable(GL.GL_DEPTH_TEST)
        if not self.root:
            return

        self.gizmo.begin(camera)
        # self.gizmo.axis(1)
        self.gizmo.ground_mark()

        # bone gizmo
        selected = None
        for bone, _ in self.root.traverse_node_and_parent(only_human_bone=True):
            assert bone.humanoid_bone
            assert bone.humanoid_tail

            color = glm.vec3(1, 1, 1)
            up = None
            width = 0.005
            height = 0.001
            if bone.humanoid_bone.get_classification().finger != Fingers.NotFinger:
                if 'Index' in bone.humanoid_bone.name or 'Ring' in bone.humanoid_bone.name:
                    if bone.humanoid_bone.name.endswith("Intermediate"):
                        color = glm.vec3(0.1, 0.4, 0.8)
                    else:
                        color = glm.vec3(0.2, 0.7, 0.9)
                else:
                    if bone.humanoid_bone.name.endswith("Intermediate"):
                        color = glm.vec3(0.8, 0.4, 0.1)
                    else:
                        color = glm.vec3(0.9, 0.7, 0.2)
                if 'Thumb' in bone.humanoid_bone.name:
                    up = glm.vec3(0, 0, 1)
                else:
                    up = glm.vec3(0, 1, 0)
            else:
                match bone.humanoid_bone:
                    case (
                        HumanoidBone.leftShoulder |
                        HumanoidBone.leftUpperArm | HumanoidBone.leftLowerArm |
                        HumanoidBone.leftUpperArm | HumanoidBone.leftLowerArm |
                        HumanoidBone.rightShoulder |
                        HumanoidBone.rightUpperArm | HumanoidBone.rightLowerArm |
                        HumanoidBone.rightUpperArm | HumanoidBone.rightLowerArm
                    ):
                        color = glm.vec3(0.3, 0.6, 0.1) if 'Lower' in bone.humanoid_bone.name else glm.vec3(
                            0.7, 0.9, 0.2)
                        up = glm.vec3(0, 0, -1)
                        width = 0.01
                        height = 0.005
                    case (HumanoidBone.leftHand | HumanoidBone.leftHand |
                            HumanoidBone.rightHand | HumanoidBone.rightHand
                          ):
                        color = glm.vec3(0.8, 0.8, 0.8)
                        up = glm.vec3(0, 1, 0)
                        width = 0.01
                        height = 0.002
                    case (HumanoidBone.head):
                        color = glm.vec3(0.8, 0.8, 0.2)
                        up = glm.vec3(0, 0, 1)
                        width = 0.06
                        height = 0.06
                    case (HumanoidBone.neck):
                        color = glm.vec3(0.4, 0.4, 0.2)
                        up = glm.vec3(0, 0, 1)
                        width = 0.02
                        height = 0.02
                    case (HumanoidBone.chest | HumanoidBone.hips):
                        color = glm.vec3(0.8, 0.8, 0.2)
                        up = glm.vec3(0, 0, 1)
                        width = 0.05
                        height = 0.04
                    case (HumanoidBone.spine):
                        color = glm.vec3(0.4, 0.4, 0.2)
                        up = glm.vec3(0, 0, 1)
                        width = 0.04
                        height = 0.03
                    case (HumanoidBone.leftUpperLeg | HumanoidBone.leftLowerLeg | HumanoidBone.leftFoot | HumanoidBone.leftToes |
                            HumanoidBone.rightUpperLeg | HumanoidBone.rightLowerLeg | HumanoidBone.rightFoot | HumanoidBone.rightToes):
                        color = glm.vec3(0.3, 0.6, 0.1)
                        if bone.humanoid_bone in (HumanoidBone.leftUpperLeg, HumanoidBone.leftFoot, HumanoidBone.rightUpperLeg, HumanoidBone.rightFoot):
                            color = glm.vec3(0.7, 0.9, 0.2)
                        up = glm.vec3(0, 0, 1)
                        width = 0.01
                        height = 0.005

            self.gizmo.matrix = (
                bone.world_matrix * glm.mat4(bone.local_axis))

            # bone
            self.gizmo.color = SELECTED_COLOR if bone == self.selected else color
            length = glm.length(
                bone.world_matrix[3].xyz - bone.humanoid_tail.world_matrix[3].xyz)

            is_selected = bone == self.selected
            if self.gizmo.bone_cube(bone.humanoid_bone.name, width, height, length, is_selected=is_selected):
                selected = bone
            if is_selected:
                # show manipulator
                self.manipulator(bone)

            # axis
            size = 0.04
            self.gizmo.color = RED
            self.gizmo.line(glm.vec3(0), glm.vec3(size, 0, 0))
            self.gizmo.color = GREEN
            self.gizmo.line(glm.vec3(0), glm.vec3(0, size, 0))
            self.gizmo.color = BLUE
            self.gizmo.line(glm.vec3(0), glm.vec3(0, 0, size))

        if selected:
            LOGGER.debug(f'selected: {selected}')
            self.selected = selected

        self.gizmo.end()

    def manipulator(self, bone: Node):
        # yaw: z
        # pitch: x
        # roll: y
        inner = 0.25
        outer = 0.3
        self.gizmo.color = glm.vec3(0, 0, 1)
        self.gizmo.ring_yaw(bone.world_matrix, inner, outer)
        self.gizmo.color = glm.vec3(1, 0, 0)
        self.gizmo.ring_pitch(bone.world_matrix, inner, outer)
        self.gizmo.color = glm.vec3(0, 1, 0)
        self.gizmo.ring_roll(bone.world_matrix, inner, outer)
