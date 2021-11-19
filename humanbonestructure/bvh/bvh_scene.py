from glglue.gl3.axis import Axis
import glglue.ctypesmath
from OpenGL import GL
from ..gl import gl_scene
from . import bvh_skeleton, bvh_parser


class BvhScene(gl_scene.Scene):
    def __init__(self):
        self.clear_color = (0.6, 0.6, 0.4, 0.0)
        self.axis = Axis(1.0 * 100)
        self.isInitialized = False
        self.skeleton = None

    def load(self, bvh: bvh_parser.Bvh):
        self.skeleton = bvh_skeleton.BvhSkeleton(bvh)

    def set_frame(self, frame: int):
        if self.skeleton:
            self.skeleton.set_frame(frame)

    def _initialize(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.isInitialized = True

    def draw(self, projection: glglue.ctypesmath.Mat4, view: glglue.ctypesmath.Mat4):
        if not self.isInitialized:
            self._initialize()
        GL.glClearColor(*self.clear_color)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT |
                   GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

        self.axis.draw(projection, view)
        if self.skeleton:
            self.skeleton.draw(projection, view)

        GL.glFlush()
