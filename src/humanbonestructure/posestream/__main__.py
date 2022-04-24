from typing import Optional
import logging
import ctypes
LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    from .tcp_listener import TcpListener
    tcp_listener = TcpListener()

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('fbo')

    from pydear import imgui as ImGui
    from pydear.utils import dockspace
    clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.3, 1)
    from pydear import glo
    fbo_manager = glo.FboRenderer()

    bg = ImGui.ImVec4(1, 1, 1, 1)
    tint = ImGui.ImVec4(1, 1, 1, 1)

    from pydear.utils.mouseevent import MouseEvent, MouseInput
    mouse_event = MouseEvent()

    def on_event(current: MouseInput, last: Optional[MouseInput]):

        if current.is_active:
            # any pressed
            clear_color[0] = current.x / current.width
            clear_color[1] = current.y / current.height
            tint.x = 1.0
        else:
            if current.is_hover:
                tint.x = 0.8
            else:
                tint.z = 0.5

    mouse_event += on_event

    def show_view(p_open):
        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (0, 0))
        if ImGui.Begin("render target", p_open,
                       ImGui.ImGuiWindowFlags_.NoScrollbar |
                       ImGui.ImGuiWindowFlags_.NoScrollWithMouse):
            w, h = ImGui.GetContentRegionAvail()
            texture = fbo_manager.clear(
                int(w), int(h), clear_color)
            if texture:
                ImGui.ImageButton(texture, (w, h), (0, 1), (1, 0), 0, bg, tint)
                from pydear import imgui_internal
                imgui_internal.ButtonBehavior(ImGui.Custom_GetLastItemRect(), ImGui.Custom_GetLastItemId(), None, None,
                                              ImGui.ImGuiButtonFlags_.MouseButtonMiddle | ImGui.ImGuiButtonFlags_.MouseButtonRight)
                io = ImGui.GetIO()
                x, y = ImGui.GetWindowPos()
                y += ImGui.GetFrameHeight()

                mouse_event.process(MouseInput(
                    (io.MousePos.x-x), (io.MousePos.y-y),
                    w, h,
                    io.MouseDown[0], io.MouseDown[1], io.MouseDown[2],
                    ImGui.IsItemActive(), ImGui.IsItemHovered(), int(io.MouseWheel)))

                if ImGui.IsItemHovered():
                    tint.z = 1.0
                else:
                    tint.z = 0.5

        ImGui.End()
        ImGui.PopStyleVar()

    from pydear.utils.loghandler import ImGuiLogHandler
    log_handler = ImGuiLogHandler()
    log_handler.register_root(append=True)

    views = [
        dockspace.Dock('tcp_listener', tcp_listener.show,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('view', show_view,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('logger', log_handler.show,
                       (ctypes.c_bool * 1)(True)),
    ]

    tcp_listener.start(app.loop)

    gui = dockspace.DockingGui(app.loop, docks=views)
    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
