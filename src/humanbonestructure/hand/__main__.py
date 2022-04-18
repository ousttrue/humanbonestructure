import logging
from pydear import imgui as ImGui

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    from pydear.utils.loghandler import ImGuiLogHandler
    log_handler = ImGuiLogHandler()
    log_handler.setFormatter(logging.Formatter(
        '%(name)s:%(lineno)s[%(levelname)s]%(message)s'))
    log_handler.register_root()

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('hello_docking')

    from pydear.utils import dockspace
    import ctypes

    from ..formats.handlandmark import HandLandmark
    hand_landmark = HandLandmark()

    views = [
        dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('landmarks', hand_landmark.show_table,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('capture', hand_landmark.capture.show,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('scene', hand_landmark.scene.show,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('hand', hand_landmark.hand.show,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('log', log_handler.draw, (ctypes.c_bool * 1)(True)),
    ]

    gui = dockspace.DockingGui(app.loop, docks=views)

    app.loop.create_task(hand_landmark.estimate())

    from pydear.backends.impl_glfw import ImplGlfwInput
    impl_glfw = ImplGlfwInput(app.window)

    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
