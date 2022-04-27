import ctypes
from pydear import imgui as ImGui
from pydear import imgui_internal
from pydear import glo
from pydear.scene.camera import Camera
from ..scene.scene import Scene


class SceneView:
    def __init__(self, name: str, scene: Scene) -> None:
        self.name = name
        self.camera = Camera(distance=8, y=-0.8)
        self.scene = scene
        # imgui
        self.clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.2, 1)
        self.hover_color = (ctypes.c_float * 4)(0.2, 0.3, 0.3, 1)
        self.fbo_manager = glo.FboRenderer()
        self.bg = ImGui.ImVec4(1, 1, 1, 1)
        self.tint = ImGui.ImVec4(1, 1, 1, 1)
        self.hover = False
        self.xy = (ctypes.c_float * 2)(0, 0)

    def show(self, p_open):
        ImGui.SetNextWindowSize((200, 200), ImGui.ImGuiCond_.Once)
        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (0, 0))
        if ImGui.Begin(self.name, p_open,
                       ImGui.ImGuiWindowFlags_.NoScrollbar |
                       ImGui.ImGuiWindowFlags_.NoScrollWithMouse):

            _w, _h = ImGui.GetContentRegionAvail()
            w = int(_w)
            h = int(_h)
            self.camera.projection.resize(w, h)

            texture = self.fbo_manager.clear(
                w, h, self.hover_color if self.hover else self.clear_color)

            if texture:
                ImGui.ImageButton(texture, (w, h), (0, 1),
                                  (1, 0), 0, self.bg, self.tint)
                imgui_internal.ButtonBehavior(ImGui.Custom_GetLastItemRect(), ImGui.Custom_GetLastItemId(), None, None,
                                              ImGui.ImGuiButtonFlags_.MouseButtonMiddle | ImGui.ImGuiButtonFlags_.MouseButtonRight)

                io = ImGui.GetIO()
                x, y = ImGui.GetWindowPos()
                y += ImGui.GetFrameHeight()
                if ImGui.IsItemActive():
                    self.camera.mouse_drag(
                        int(io.MousePos.x-x), int(io.MousePos.y-y),
                        int(io.MouseDelta.x), int(io.MouseDelta.y),
                        io.MouseDown[0], io.MouseDown[1], io.MouseDown[2])
                else:
                    self.camera.mouse_release(
                        int(io.MousePos.x-x), int(io.MousePos.y-y))

                self.hover = ImGui.IsItemHovered()
                if self.hover:
                    self.camera.wheel(int(io.MouseWheel))

                # render mesh
                self.scene.render(self.camera)

        ImGui.End()
        ImGui.PopStyleVar()
