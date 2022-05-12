from typing import Optional, Iterable
import logging
import math
from OpenGL import GL
import glm
from pydear.scene.camera import Camera
from pydear.gizmo.gizmo import Gizmo
from pydear.gizmo.shapes.shape import Shape, ShapeState
from pydear.gizmo.shapes.ring_shape import RingShape
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
        self.shape_node_map = {}
        self.selected = None
        #
        self.gizmo = Gizmo()
        self.setup_drag()

    def setup_drag(self):
        # draggable
        ring = RingShape(inner=0.1, outer=0.2, depth=0.005,
                         color=glm.vec4(0.3, 0.3, 1, 1))
        self.ring_key = self.gizmo.add_shape(ring)

        def on_selected(shape: Optional[Shape]):
            if shape:
                ring.remove_state(ShapeState.HIDE)
                ring.matrix.set(shape.matrix.value)
                self.selected = self.shape_node_map.get(shape)
            else:
                ring.add_state(ShapeState.HIDE)
                self.selected = None

        self.gizmo.selected += on_selected

    def set_skeleton(self, skeleton: Optional[HumanoidSkeleton]):
        self.skeleton = skeleton
        if self.skeleton:
            # setup node
            self.root = self.skeleton.to_node()
            self.root.init_human_bones()
            for bone, _ in self.root.traverse_node_and_parent():
                if bone.humanoid_bone.is_enable():
                    bone.local_axis = glm.quat(
                        bone.humanoid_bone.get_classification().get_local_axis())
            self.root.calc_world_matrix(glm.mat4())

            # setup gizmo
            from .bone_shape import BoneShape
            for bone in HumanoidBone:
                if bone.is_enable():
                    node = self.root.find_humanoid_bone(bone)
                    if node:
                        shape = BoneShape.from_node(node)
                        self.gizmo.add_shape(shape)
                        self.shape_node_map[shape] = node

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

    def render(self, camera: Camera, x: int, y: int):
        GL.glEnable(GL.GL_DEPTH_TEST)
        if not self.root:
            return

        self.gizmo.process(camera, x, y)
