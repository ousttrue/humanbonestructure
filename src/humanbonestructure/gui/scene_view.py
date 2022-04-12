import ctypes
from pydear import imgui as ImGui
from pydear import glo
from ..scene import Scene


class SceneView:
    def __init__(self, name: str, scene: Scene) -> None:
        self.name = name
        self.scene = scene
        self.clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.3, 1)
        self.hover_color = (ctypes.c_float * 4)(0.2, 0.4, 0.6, 1)
        self.fbo_manager = glo.FboRenderer()

    def show(self, p_open):
        ImGui.SetNextWindowSize((200, 200), ImGui.ImGuiCond_.Once)
        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (0, 0))
        if ImGui.Begin(self.name, p_open,
                       ImGui.ImGuiWindowFlags_.NoScrollbar |
                       ImGui.ImGuiWindowFlags_.NoScrollWithMouse):

            _w, _h = ImGui.GetContentRegionAvail()
            w = int(_w)
            h = int(_h)

            texture = self.fbo_manager.clear(
                w, h, self.hover_color if self.scene.hover else self.clear_color)
            if texture:
                # render mesh
                self.scene.render(w, h)

                ImGui.BeginChild("_image_")
                ImGui.Image(texture, (w, h), (0, 1), (1, 0))
                self.scene.hover = ImGui.IsItemHovered()
                ImGui.EndChild()
        ImGui.End()
        ImGui.PopStyleVar()
