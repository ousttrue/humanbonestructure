import glglue.basecontroller
from glglue.gl3.axis import Axis
import glglue.ctypesmath
from OpenGL import GL
from . import bvh_skeleton
from . import bvh_parser


class BvhController(glglue.basecontroller.BaseController):
    def __init__(self):
        self.clear_color = (0.6, 0.6, 0.4, 0.0)
        self.axis = Axis(1.0 * 100)
        self.camera = glglue.ctypesmath.Camera()
        self.camera.projection.z_far *= 100
        self.camera.view.distance *= 100
        self.isInitialized = False
        self.skeleton = None

    def load(self, bvh: bvh_parser.Bvh):
        self.skeleton = bvh_skeleton.BvhSkeleton(bvh)

    def set_frame(self, frame: int):
        if self.skeleton:
            self.skeleton.set_frame(frame)

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

    def draw(self):
        if not self.isInitialized:
            self.initialize()
        GL.glClearColor(*self.clear_color)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.axis.draw(self.camera.projection.matrix, self.camera.view.matrix)
        if self.skeleton:
            self.skeleton.draw(self.camera.projection.matrix,
                               self.camera.view.matrix)

        GL.glFlush()
