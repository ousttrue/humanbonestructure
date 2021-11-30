from OpenGL import GL
import glglue.ctypesmath
from ..gl import gl_scene
from . import bvh_skeleton, bvh_parser


class BvhScene(gl_scene.Scene):
    def __init__(self):
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

        if self.skeleton:
            self.skeleton.draw(projection, view)
