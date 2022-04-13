import ctypes
from pydear import glo
from pydear import imgui as ImGui
from pydear.scene.camera import Camera


class HandScene:
    def __init__(self) -> None:
        self.clear_color = (ctypes.c_float * 4)(0.2, 0.1, 0.1, 1)
        self.fbo_manager = glo.FboRenderer()
        self.camera = Camera(distance=0.2)
        from .axis import Axis
        self.axis = Axis()
        # gui
        self.hover = False

    def show(self, p_open):
        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (0, 0))
        if ImGui.Begin("hand", p_open,
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
                # self.hand.render(self.camera)

                ImGui.BeginChild("_image_")
                ImGui.Image(texture, (w, h), (0, 1), (1, 0))
                self.hover = ImGui.IsItemHovered()
                ImGui.EndChild()
        ImGui.End()
        ImGui.PopStyleVar()
