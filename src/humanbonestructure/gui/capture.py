import numpy
from typing import Optional, List
import ctypes
from OpenGL import GL
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
from pydear import glo
from pydear import imgui as ImGui


class Float3(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float),
    ]


class Point(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('color', Float3),
    ]


class RectVertex(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('u', ctypes.c_float),
        ('v', ctypes.c_float),
    ]


RECT_VERTICES = (RectVertex * 4)(
    RectVertex(-1, 1, 0, 0),
    RectVertex(-1, -1, 0, 1),
    RectVertex(1, -1, 1, 1),
    RectVertex(1, 1, 1, 0),
)

RECT_INDICES = (ctypes.c_uint16 * 6)(
    0, 1, 2,
    2, 3, 0,
)


class Points:
    def __init__(self) -> None:
        self.vertices = (Point * 512)()
        self.is_updated = False
        self.draw_count = 0
        self.shader: Optional[glo.Shader] = None
        self.vao: Optional[glo.Vao] = None

    def update(self, results):
        # update vertices
        self.draw_count = 0
        self.is_updated = True
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_class = handedness.classification[0]

                # 右手が赤
                color = Float3(
                    1, 0, 0) if hand_class.label == 'Left' else Float3(0, 0, 1)

                for v in hand_landmarks.landmark:
                    self.vertices[self.draw_count] = Point(
                        v.x * 2 - 1, (1-v.y) * 2 - 1, color)
                    self.draw_count += 1

    def render(self):
        if not self.shader:
            self.shader = glo.Shader.load_from_pkg(
                'humanbonestructure', 'assets/point')
            if not self.shader:
                return
            vbo = glo.Vbo()
            vbo.set_vertices(self.vertices, is_dynamic=True)
            self.vao = glo.Vao(
                vbo, glo.VertexLayout.create_list(self.shader.program))
            self.is_updated = 0
        assert self.vao

        if self.is_updated:
            self.vao.vbo.set_vertices(self.vertices, is_dynamic=True)
            self.is_updated = False

        with self.shader:
            GL.glPointSize(10)
            self.vao.draw(self.draw_count, topology=GL.GL_POINTS)


class Rect:
    def __init__(self) -> None:
        self.vao = None
        self.shader = None
        self.texture = None
        self.image = None

    def set_image(self, image):
        self.image = image

    def render(self):
        if not self.shader:
            self.shader = glo.Shader.load_from_pkg(
                'humanbonestructure', 'assets/rect')
            if not self.shader:
                return

            vbo = glo.Vbo()
            vbo.set_vertices(RECT_VERTICES)

            ibo = glo.Ibo()
            ibo.set_indices(RECT_INDICES)

            self.vao = glo.Vao(
                vbo, glo.VertexLayout.create_list(self.shader.program), ibo)
        assert self.vao

        if self.image is not None:
            h, w = self.image.shape[:2]
            if not self.texture or self.texture.width != w or self.texture.height != h:
                self.texture = glo.Texture(
                    w, h, self.image, pixel_type=GL.GL_RGB)
            else:
                self.texture.update(0, 0, w, h, self.image)
            self.image = None

        with self.shader:
            if self.texture:
                self.texture.bind()
            self.vao.draw(len(RECT_INDICES), topology=GL.GL_TRIANGLES)


class CaptureView:
    def __init__(self) -> None:
        self.clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.3, 1)
        self.fbo_manager = glo.FboRenderer()
        self.rect = Rect()
        self.points = Points()

    def show(self, p_open):
        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (0, 0))
        if ImGui.Begin("capture", p_open,
                       ImGui.ImGuiWindowFlags_.NoScrollbar |
                       ImGui.ImGuiWindowFlags_.NoScrollWithMouse):
            w, h = ImGui.GetContentRegionAvail()
            texture = self.fbo_manager.clear(
                int(w), int(h), self.clear_color)

            if texture:
                self.rect.render()
                self.points.render()

                ImGui.BeginChild("_image_")
                ImGui.Image(texture, (w, h), (0, 1), (1, 0))
                ImGui.EndChild()
        ImGui.End()
        ImGui.PopStyleVar()
