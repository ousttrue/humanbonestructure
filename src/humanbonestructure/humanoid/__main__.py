from typing import Optional
import logging
import ctypes
from OpenGL import GL
import glm
from pydear import imgui as ImGui
from pydear.scene.camera import Camera
from pydear.scene.gizmo import Gizmo
from . import humanoid

LOGGER = logging.getLogger(__name__)


class HumanoidView:
    def __init__(self, root):
        self.clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.3, 1)
        from pydear import glo
        self.fbo_manager = glo.FboRenderer()

        self.bg = ImGui.ImVec4(1, 1, 1, 1)
        self.tint = ImGui.ImVec4(1, 1, 1, 1)

        self.camera = Camera(y=-1.0, distance=5.0)

        self.root = root
        self.gizmo = Gizmo()
        self.selected: Optional[humanoid.Bone] = None

    def _draw(self, bone: humanoid.Bone, parent: glm.mat4):
        matrix = parent * bone.local_init_matrix * bone.local_euler_matrix()

        for i, child in enumerate(bone.children):
            if i == 0:
                self.gizmo.matrix = glm.mat4(*matrix)
                # self.gizmo.matrix = bone.world_matrix
                if self.gizmo.bone(bone.bone, glm.length(child.offset), bone == self.selected):
                    if self.selected != bone:
                        self.selected = bone
                        # self.on_selected(self.selected)

            self._draw(child, matrix)

    def draw(self, x, y, left):
        GL.glClearColor(*self.clear_color)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT |
                   GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

        GL.glViewport(0, 0, self.camera.projection.width,
                      self.camera.projection.height)

        # GL.glEnable(GL.GL_DEPTH_TEST)

        self.gizmo.begin(
            x,
            y,
            left,
            self.camera.view.matrix,
            self.camera.projection.matrix,
            self.camera.get_mouse_ray(x, y))

        self.gizmo.axis(10)
        self._draw(self.root, glm.mat4())

        self.gizmo.end()

    def show(self, p_open):
        ImGui.SetNextWindowSize((200, 200), ImGui.ImGuiCond_.FirstUseEver)
        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (0, 0))
        if ImGui.Begin("render target", p_open,
                       ImGui.ImGuiWindowFlags_.NoScrollbar |
                       ImGui.ImGuiWindowFlags_.NoScrollWithMouse):
            w, h = ImGui.GetContentRegionAvail()
            texture = self.fbo_manager.clear(
                int(w), int(h), self.clear_color)
            if texture:
                self.camera.projection.resize(int(w), int(h))
                ImGui.ImageButton(texture, (w, h), (0, 1),
                                  (1, 0), 0, self.bg, self.tint)
                from pydear import imgui_internal
                imgui_internal.ButtonBehavior(ImGui.Custom_GetLastItemRect(), ImGui.Custom_GetLastItemId(), None, None,
                                              ImGui.ImGuiButtonFlags_.MouseButtonMiddle | ImGui.ImGuiButtonFlags_.MouseButtonRight)
                io = ImGui.GetIO()
                x, y = ImGui.GetWindowPos()
                y += ImGui.GetFrameHeight()
                x, y = int(io.MousePos.x-x), int(io.MousePos.y-y)
                if ImGui.IsItemActive():

                    self.camera.mouse_drag(
                        x, y,
                        int(io.MouseDelta.x), int(io.MouseDelta.y),
                        io.MouseDown[0], io.MouseDown[1], io.MouseDown[2])
                else:
                    self.camera.mouse_release()

                if ImGui.IsItemHovered():
                    self.camera.wheel(io.MouseWheel)

                self.draw(x, y, io.MouseDown[0])

        ImGui.End()
        ImGui.PopStyleVar()


def main():
    logging.basicConfig(level=logging.DEBUG)

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('fbo')

    root = humanoid.make_humanoid(1.0)
    # tree
    # prop
    # view
    view = HumanoidView(root)

    from pydear.utils import dockspace
    views = [
        dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('view', view.show,
                       (ctypes.c_bool * 1)(True)),
    ]

    gui = dockspace.DockingGui(app.loop, docks=views)
    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
