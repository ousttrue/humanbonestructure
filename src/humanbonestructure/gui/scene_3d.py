from typing import Optional
import ctypes
from OpenGL import GL
import glm
from pydear import imgui as ImGui
from pydear import glo
from pydear.scene.camera import Camera


class Float3(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float),
    ]


class HandVertex(ctypes.Structure):
    _fields_ = [
        ('pos', Float3),
        ('rgb', Float3),
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
        self.vertices = (HandVertex * 512)()
        self.hand_count = 0
        self.is_updated = False

    def update(self, results):
        # update vertices

        i = 0
        self.hand_count = 0
        if results.multi_hand_world_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_world_landmarks, results.multi_handedness):
                hand_class = handedness.classification[0]

                # 右手が赤
                color = Float3(
                    1, 0, 0) if hand_class.label == 'Left' else Float3(0, 0, 1)

                for v in hand_landmarks.landmark:
                    self.vertices[i] = HandVertex(Float3(v.x, -v.y, -v.z), color)
                    i += 1
                self.hand_count += 1
        self.is_updated = True

    def render(self, camera: Camera):
        if not self.shader:
            self.shader = glo.Shader.load_from_pkg(
                'humanbonestructure', 'assets/hand')
            assert self.shader
            self.props = self.shader.create_props(camera)

            vbo = glo.Vbo()
            vbo.set_vertices(self.vertices, is_dynamic=True)

            ibo = glo.Ibo()
            indices = []
            vertex_offset = 0
            for i in range(5):
                for j in HAND_INDICES:
                    indices.append(j + vertex_offset)
                vertex_offset += 21
            ibo.set_indices(
                (ctypes.c_uint16 * len(indices))(*indices))

            self.vao = glo.Vao(
                vbo, glo.VertexLayout.create_list(self.shader.program), ibo)
            self.is_updated = False
        assert self.vao

        if self.is_updated:
            self.vao.vbo.set_vertices(self.vertices, is_dynamic=True)
            self.is_updated = False

        with self.shader:
            for prop in self.props:
                prop()

            self.vao.draw(len(HAND_INDICES) * self.hand_count,
                          topology=GL.GL_LINES)


class Scene3D:
    def __init__(self) -> None:
        self.clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.1, 1)
        self.fbo_manager = glo.FboRenderer()
        self.camera = Camera(distance=1)
        from ..scene.gizmo import Gizmo
        self.axis = Gizmo()
        self.hand = Hand()
        # gui
        self.hover = False

    def show(self, p_open):
        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (0, 0))
        if ImGui.Begin("scene", p_open,
                       ImGui.ImGuiWindowFlags_.NoScrollbar |
                       ImGui.ImGuiWindowFlags_.NoScrollWithMouse):
            w, h = ImGui.GetContentRegionAvail()
            self.camera.onResize(w, h)
            if self.hover:
                x, y = ImGui.GetWindowPos()
                y += ImGui.GetFrameHeight()
                io = ImGui.GetIO()
                self.camera.drag(io.MousePos.x-x, io.MousePos.y-y, int(io.MouseDelta.x), int(io.MouseDelta.y),
                                 io.MouseDown[0], io.MouseDown[1], io.MouseDown[2])
                self.camera.onWheel(int(io.MouseWheel))

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
