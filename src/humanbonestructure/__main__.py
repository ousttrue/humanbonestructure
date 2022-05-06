from typing import Optional
from pydear.utils import dockspace
from pydear import imgui as ImGui
import asyncio
import ctypes
import logging
import pathlib
import argparse
from pydear.utils.setting import BinSetting
LOGGER = logging.getLogger(__name__)


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop, *, setting: Optional[BinSetting] = None, nerdfont_path: Optional[pathlib.Path] = None) -> None:
        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        # from .scene.scene import Scene
        # self.scene = Scene('view')
        # from .gui.scene_view import SceneView
        # self.view = SceneView('view', self.scene)
        # dockspace.Dock('view', self.view.show,
        #                (ctypes.c_bool * 1)(True)),

        from .gui.pose_graph.pose_graph_editor import PoseGraphEditor
        self.node_editor = PoseGraphEditor(setting=setting)

        self.docks = [
            dockspace.Dock('posegraph', self.node_editor.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('logger', log_handler.show,
                           (ctypes.c_bool * 1)(True)),
        ]

        self.nerdfont_path = nerdfont_path
        super().__init__(loop, docks=self.docks, setting=setting)

    def _setup_font(self):
        io = ImGui.GetIO()
        # font load
        from pydear.utils import fontloader
        fontloader.load(pathlib.Path(
            'C:/Windows/Fonts/MSGothic.ttc'), 20.0, io.Fonts.GetGlyphRangesJapanese())  # type: ignore

        if self.nerdfont_path and self.nerdfont_path.exists():
            from pydear.utils import nerdfont
            font_range = nerdfont.create_font_range()
            fontloader.load(self.nerdfont_path, 20.0,
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
    parser.add_argument('--asset', type=pathlib.Path)
    parser.add_argument('--nerdfont', type=pathlib.Path)
    args = parser.parse_args()

    setting = None
    if args.ini:
        from pydear.utils.setting import BinSetting
        setting = BinSetting(args.ini)

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('humanbonestructure', setting=setting)

    gui = GUI(app.loop, setting=setting, nerdfont_path=args.nerdfont)

    if args.asset:
        gui.node_editor.graph.current_dir = args.asset

    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()

    if setting:
        gui.node_editor.save()
        gui.save()
        app.save()
        setting.save()


if __name__ == '__main__':
    main()
