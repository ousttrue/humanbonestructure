import glglue.basecontroller
from glglue.ctypesmath import Camera, Mat4
from glglue.gl3 import gizmo
from OpenGL import GL
from dataclasses import dataclass
from ..gl import gl_scene
from . import humanoid


class HumanoidScene(gl_scene.Scene):
    def __init__(self, root: humanoid.Bone):
        self.isInitialized = False
        self.root = root
        self.gizmo = gizmo.Gizmo()

    def _initialize(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.isInitialized = True

    def _draw(self, bone: humanoid.Bone, parent):
        m = Mat4.new_translation(
            *bone.offset) * parent

        self.gizmo.axis(0.1, m)

        for child in bone.children:
            self._draw(child, m)

    def draw(self, camera: Camera):
        if not self.isInitialized:
            self._initialize()

        self.gizmo.begin(camera.view.matrix * camera.projection.matrix)

        m = Mat4.new_identity()
        self.gizmo.axis(10, m)
        self._draw(self.root, m)

        self.gizmo.end()
