import glglue.basecontroller
import glglue.ctypesmath
import glglue.gl3.axis
from OpenGL import GL
from dataclasses import dataclass
from ..gl import gl_scene
from . import humanoid


@dataclass
class Drawable:
    bone: humanoid.Bone
    matrix: glglue.ctypesmath.Mat4
    axis: glglue.gl3.axis.Axis

    def draw(self, proj, view):
        self.axis.draw(proj, self.matrix * view)


class HumanoidScene(gl_scene.Scene):
    def __init__(self, root: humanoid.Bone):
        self.isInitialized = False
        self.root = root
        self.bone_map = {
            bone: Drawable(
                bone, glglue.ctypesmath.Mat4.new_identity(), glglue.gl3.axis.Axis(0.1))for bone in self.root.traverse()
        }

    def _initialize(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.isInitialized = True

    def _update(self, bone: humanoid.Bone, parent):
        d = self.bone_map[bone]
        d.matrix = glglue.ctypesmath.Mat4.new_translation(
            *bone.offset) * parent
        for child in bone.children:
            self._update(child, d.matrix)

    def draw(self, projection, view):
        if not self.isInitialized:
            self._initialize()

        self._update(self.root, glglue.ctypesmath.Mat4.new_identity())
        for bone, d in self.bone_map.items():
            d.draw(projection, view)
