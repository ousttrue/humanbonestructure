from typing import Optional
from OpenGL import GL
from pydear.scene.camera import Camera
from glglue.ctypesmath import Mat4, Float3, Float4, FrameState
from glglue.gl3 import gizmo
from ..gl import gl_scene
from . import humanoid


class HumanoidScene:
    def __init__(self, root: humanoid.Bone, on_selected):
        self.isInitialized = False
        self.root = root
        self.gizmo = gizmo.Gizmo()
        self.selected: Optional[humanoid.Bone] = None
        self.on_selected = on_selected

    def _initialize(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.isInitialized = True

    def _draw(self, bone: humanoid.Bone, parent: Mat4):
        matrix = bone.local_euler_matrix() * bone.local_init_matrix * parent

        for i, child in enumerate(bone.children):
            if i == 0:
                self.gizmo.matrix = matrix
                # self.gizmo.matrix = bone.world_matrix
                if self.gizmo.bone(bone.bone, child.offset.get_length(), bone == self.selected):
                    if self.selected != bone:
                        self.selected = bone
                        self.on_selected(self.selected)

            self._draw(child, matrix)

    def draw(self, state: FrameState):
        if not self.isInitialized:
            self._initialize()

        self.gizmo.begin(state)

        self.gizmo.axis(10)
        self._draw(self.root, Mat4.new_identity())

        self.gizmo.end()
