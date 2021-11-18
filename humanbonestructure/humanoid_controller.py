import glglue.basecontroller
import glglue.ctypesmath
import glglue.gl3.axis
from OpenGL import GL
from . import humanoid
from dataclasses import dataclass


@dataclass
class Drawable:
    bone: humanoid.Bone
    matrix: glglue.ctypesmath.Mat4
    axis: glglue.gl3.axis.Axis

    def draw(self, proj, view):
        self.axis.draw(proj, self.matrix * view)


class HumanoidController(glglue.basecontroller.BaseController):
    def __init__(self, root: humanoid.Bone):
        self.clear_color = (0.4, 0.6, 0.6, 0.0)
        self.camera = glglue.ctypesmath.Camera()
        self.isInitialized = False

        self.root = root
        self.bone_map = {
            bone: Drawable(
                bone, glglue.ctypesmath.Mat4.new_identity(), glglue.gl3.axis.Axis(0.1))for bone in self.root.traverse()
        }

    def onResize(self, w: int, h: int) -> bool:
        GL.glViewport(0, 0, w, h)
        return self.camera.onResize(w, h)

    def onLeftDown(self, x: int, y: int) -> bool:
        """mouse input"""
        return self.camera.onLeftDown(x, y)

    def onLeftUp(self, x: int, y: int) -> bool:
        """mouse input"""
        return self.camera.onLeftUp(x, y)

    def onMiddleDown(self, x: int, y: int) -> bool:
        """mouse input"""
        return self.camera.onMiddleDown(x, y)

    def onMiddleUp(self, x: int, y: int) -> bool:
        """mouse input"""
        return self.camera.onMiddleUp(x, y)

    def onRightDown(self, x: int, y: int) -> bool:
        """mouse input"""
        return self.camera.onRightDown(x, y)

    def onRightUp(self, x: int, y: int) -> bool:
        """mouse input"""
        return self.camera.onRightUp(x, y)

    def onMotion(self, x: int, y: int) -> bool:
        """mouse input"""
        return self.camera.onMotion(x, y)

    def onWheel(self, d: int) -> bool:
        """mouse input"""
        return self.camera.onWheel(d)

    def onKeyDown(self, keycode: int) -> bool:
        return False

    def onUpdate(self, d: int) -> bool:
        """
        milliseconds
        """
        return False

    def initialize(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.isInitialized = True

    def _update(self, bone: humanoid.Bone, parent):
        d = self.bone_map[bone]
        d.matrix = glglue.ctypesmath.Mat4.new_translation(
            *bone.offset) * parent
        for child in bone.children:
            self._update(child, d.matrix)

    def draw(self):
        if not self.isInitialized:
            self.initialize()
        GL.glClearColor(*self.clear_color)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT |
                   GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

        self._update(self.root, glglue.ctypesmath.Mat4.new_identity())

        for bone, d in self.bone_map.items():
            d.draw(self.camera.projection.matrix, self.camera.view.matrix)

        GL.glFlush()
