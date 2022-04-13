from typing import Optional
import ctypes
from OpenGL import GL
import glm
from pydear import imgui as ImGui
from pydear import glo
from pydear.scene.camera import Camera


class HandVertex(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float),
    ]


HAND_INDICES = [
    0, 1,
    1, 2,
    2, 3,
    3, 4,

    0, 5,
    5, 6,
    6, 7,
    7, 8,

    0, 9,
    9, 10,
    10, 11,
    11, 12,

    0, 13,
    13, 14,
    14, 15,
    15, 16,

    0, 17,
    17, 18,
    18, 19,
    19, 20,

    5, 9,
    9, 13,
    13, 17,
]


class Hand:
    def __init__(self) -> None:
        self.shader: Optional[glo.Shader] = None
        self.vao: Optional[glo.Vao] = None
        self.vertices = (HandVertex * 21)()
        self.is_updated = False

    def update(self, landmark):
        for i, v in enumerate(landmark):
            self.vertices[i] = HandVertex(v.x, -v.y, -v.z)
        self.is_updated = True

    def render(self, camera: Camera):
        if not self.shader:
            self.shader = glo.Shader.load_from_pkg('humanbonestructure', 'assets/hand')
            assert self.shader

            view = glo.UniformLocation.create(self.shader.program, "uView")
            projection = glo.UniformLocation.create(
                self.shader.program, "uProjection")
            self.props = [
                glo.ShaderProp(
                    lambda x: view.set_mat4(x),
                    lambda:glm.value_ptr(camera.view.matrix)),
                glo.ShaderProp(
                    lambda x: projection.set_mat4(x),
                    lambda:glm.value_ptr(camera.projection.matrix)),
            ]

            vbo = glo.Vbo()
            vbo.set_vertices(self.vertices, is_dynamic=True)

            ibo = glo.Ibo()
            ibo.set_indices(
                (ctypes.c_uint16 * len(HAND_INDICES))(*HAND_INDICES))

            self.vao = glo.Vao(
                vbo, glo.VertexLayout.create_list(self.shader.program), ibo)
            self.is_updated = False
        assert self.vao

        if self.is_updated:
            self.vao.vbo.set_vertices(self.vertices, is_dynamic=True)
            self.is_updated = False

        with self.shader:
            for prop in self.props:
                prop.update()

            self.vao.draw(len(HAND_INDICES), topology=GL.GL_LINES)


class Scene:
    def __init__(self) -> None:
        self.clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.1, 1)
        self.fbo_manager = glo.FboRenderer()
        self.camera = Camera(distance=0.2)
        from .axis import Axis
        self.axis = Axis()
        self.hand = Hand()
        # gui
        self.hover = False

    def show(self, p_open):
        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (0, 0))
        if ImGui.Begin("scene", p_open,
                       ImGui.ImGuiWindowFlags_.NoScrollbar |
                       ImGui.ImGuiWindowFlags_.NoScrollWithMouse):
            w, h = ImGui.GetContentRegionAvail()
            if self.hover:
                x, y = ImGui.GetWindowPos()
                y += ImGui.GetFrameHeight()
                io = ImGui.GetIO()
                self.camera.update(w, h, io.MousePos.x-x, io.MousePos.y-y,
                                   io.MouseDown[0], io.MouseDown[1], io.MouseDown[2], int(io.MouseWheel))

            texture = self.fbo_manager.clear(
                int(w), int(h), self.clear_color)

            if texture:
                self.axis.render(self.camera)
                self.hand.render(self.camera)

                ImGui.BeginChild("_image_")
                ImGui.Image(texture, (w, h), (0, 1), (1, 0))
                self.hover = ImGui.IsItemHovered()
                ImGui.EndChild()
        ImGui.End()
        ImGui.PopStyleVar()
