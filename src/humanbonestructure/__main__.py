from typing import Optional
from pydear.utils import dockspace
from pydear import imgui as ImGui
import asyncio
import ctypes
import logging
import pathlib
import argparse
from pydear.utils.setting import SettingInterface
LOGGER = logging.getLogger(__name__)


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop, *, setting: Optional[SettingInterface] = None) -> None:
        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        # from .scene.scene import Scene
        # self.scene = Scene('view')
        # from .gui.scene_view import SceneView
        # self.view = SceneView('view', self.scene)
        # dockspace.Dock('view', self.view.show,
        #                (ctypes.c_bool * 1)(True)),

        from .gui.pose_graph.graph import PoseGraph
        self.graph = PoseGraph(setting=setting)

        

        self.docks = [
            dockspace.Dock('posegraph', self.graph.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('logger', log_handler.show,
                           (ctypes.c_bool * 1)(True)),
        ]

        super().__init__(loop, docks=self.docks, setting=setting)

    def _setup_font(self):
        io = ImGui.GetIO()
        # font load
        from pydear.utils import fontloader
        fontloader.load(pathlib.Path(
            'C:/Windows/Fonts/MSGothic.ttc'), 20.0, io.Fonts.GetGlyphRangesJapanese())  # type: ignore
        import fontawesome47
        font_range = (ctypes.c_ushort * 3)(*fontawesome47.RANGE, 0)
        fontloader.load(fontawesome47.get_path(), 20.0,
                        font_range, merge=True, monospace=True)

        io.Fonts.Build()


def main():
    '''
    node
    '''
    logging.basicConfig(level=logging.DEBUG)

    # args
    parser = argparse.ArgumentParser()
    parser.add_argument('--ini', type=pathlib.Path)
    args = parser.parse_args()

    setting = None
    if args.ini:
        from pydear.utils.setting import TomlSetting
        setting = TomlSetting(args.ini)

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('humanbonestructure', setting=setting)

    gui = GUI(app.loop, setting=setting)

    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()

    if setting:
        gui.graph.save()
        gui.save()
        app.save()
        setting.write()


if __name__ == '__main__':
    main()
