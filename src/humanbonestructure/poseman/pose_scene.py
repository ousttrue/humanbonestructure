from typing import Optional
import logging
import glm
from pydear.scene.camera import Camera
from pydear.scene.gizmo import Gizmo
from ..humanoid.humanoid_skeleton import HumanoidSkeleton

LOGGER = logging.getLogger(__name__)
RED = glm.vec4(1, 0, 0, 1)
GREEN = glm.vec4(0, 1, 0, 1)
BLUE = glm.vec4(0, 0, 1, 1)


class PoseScene:
    def __init__(self) -> None:
        self.skeleton = None
        self.root = None
        self.selected = None
        #
        self.gizmo = Gizmo()

    def set_skeleton(self, skeleton: Optional[HumanoidSkeleton]):
        self.skeleton = skeleton
        if self.skeleton:
            self.root = self.skeleton.to_node()
            self.root.init_human_bones()
            self.root.calc_world_matrix(glm.mat4())
        else:
            self.root = None

    def get_root(self):
        return self.root

    def get_selected(self):
        return self.selected

    def set_selected(self, selected):
        self.selected = selected

    def show_option(self):
        pass

    def render(self, camera: Camera):
        if not self.root:
            return

        self.gizmo.begin(camera.x, camera.y, camera.left, camera.view.matrix,
                         camera.projection.matrix, camera.get_mouse_ray(camera.x, camera.y))
        # self.gizmo.axis(1)
        self.gizmo.ground_mark()

        # bone gizmo
        selected = None
        for bone, _ in self.root.traverse_node_and_parent(only_human_bone=True):
            assert bone.humanoid_bone
            assert bone.humanoid_tail
            # bone
            if self.gizmo.bone_head_tail(bone.humanoid_bone.name,
                                         bone.world_matrix[3].xyz, bone.humanoid_tail.world_matrix[3].xyz, glm.vec3(
                                             0, 0, 1),
                                         is_selected=(bone == self.selected)):
                selected = bone

            # axis
            self.gizmo.matrix = (
                bone.world_matrix * glm.mat4(bone.local_axis))
            self.gizmo.color = RED
            self.gizmo.line(glm.vec3(0), glm.vec3(0.02, 0, 0))
            self.gizmo.color = GREEN
            self.gizmo.line(glm.vec3(0), glm.vec3(0, 0.02, 0))
            self.gizmo.color = BLUE
            self.gizmo.line(glm.vec3(0), glm.vec3(0, 0, 0.02))

        if selected:
            LOGGER.debug(f'selected: {selected}')
            self.selected = selected

        self.gizmo.end()
