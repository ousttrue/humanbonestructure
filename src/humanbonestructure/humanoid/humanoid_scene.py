from typing import Optional
from OpenGL import GL
from glglue.ctypesmath import Camera, Mat4, Float3, Float4
from glglue.gl3 import gizmo
from ..gl import gl_scene
from . import humanoid


class HumanoidScene(gl_scene.Scene):
    def __init__(self, root: humanoid.Bone):
        self.isInitialized = False
        self.root = root
        self.gizmo = gizmo.Gizmo()
        self.selected: Optional[humanoid.Bone] = None

    def _initialize(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.isInitialized = True

    def _draw(self, bone: humanoid.Bone):
        self.gizmo.matrix = bone.world_matrix

        # self.gizmo.axis(0.1, m)
        if bone.children:
            tail = bone.children[0]
            length = tail.offset.get_length()
            s = length * 0.1
            # head-tail
            #      0, -1(p1)
            # (p2)  |
            # -1, 0 |
            #     --+--->
            #       |    1, 0(p0)
            #       v
            #      0, +1(p3)
            self.gizmo.color = Float4(1, 0.0, 1, 1)
            h = Float3(0, 0, 0)
            t = Float3(0, length, 0)
            # self.gizmo.line(h, t, bone.world_matrix)
            p0 = Float3(s, s, 0)
            p1 = Float3(0, s, -s)
            p2 = Float3(-s, s, 0)
            p3 = Float3(0, s, s)

            self.gizmo.line(p0, p1)
            self.gizmo.line(p1, p2)
            self.gizmo.line(p2, p3)
            self.gizmo.line(p3, p0)

            # self.gizmo.line(p2, p0, bone.world_matrix)
            self.gizmo.color = Float4(1, 0, 0, 1)
            self.gizmo.line(h, p0)
            self.gizmo.line(p0, t)
            self.gizmo.color = Float4(0.1, 0, 0, 1)
            if bone == self.selected:
                self.gizmo.color = Float4(0.1, 1, 0, 1)
            self.gizmo.line(h, p2)
            self.gizmo.line(p2, t)

            # self.gizmo.line(p1, p3, bone.world_matrix)
            self.gizmo.color = Float4(0, 0, 1, 1)
            self.gizmo.line(h, p3)
            self.gizmo.line(p3, t)
            self.gizmo.color = Float4(0, 0, 0.1, 1)
            if bone == self.selected:
                self.gizmo.color = Float4(0, 1, 0.1, 1)
            self.gizmo.line(h, p1)
            self.gizmo.line(p1, t)

        for child in bone.children:
            self._draw(child)

    def draw(self, camera: Camera):
        if not self.isInitialized:
            self._initialize()

        self.gizmo.begin(camera.view.matrix, camera.projection.matrix)

        self.gizmo.axis(10)
        self._draw(self.root)

        self.gizmo.end()
