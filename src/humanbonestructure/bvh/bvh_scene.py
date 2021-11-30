from OpenGL import GL
from glglue.ctypesmath import Camera
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

    def draw(self, camera: Camera):
        if not self.isInitialized:
            self._initialize()

        if self.skeleton:
            self.skeleton.draw(camera.projection.matrix, camera.view.matrix)

    def expand_aabb(self, aabb):
        return aabb
