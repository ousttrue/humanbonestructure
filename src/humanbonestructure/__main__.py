from typing import Optional
import asyncio
import ctypes
import logging
import pathlib
import argparse
from pydear.utils import dockspace
from pydear import imgui as ImGui
from pydear.utils.setting import BinSetting
from pydear.utils.node_editor.editor import NodeEditor
LOGGER = logging.getLogger(__name__)


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop, *, setting: Optional[BinSetting] = None, nerdfont_path: Optional[pathlib.Path] = None) -> None:
        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        self.node_editor = NodeEditor('posegraph', setting=setting)
        from .gui.pose_graph import TYPES, PIN_STYLE_MAP
        for t in TYPES:
            self.node_editor.graph.register_type(t)
        for k, v in PIN_STYLE_MAP.items():
            self.node_editor.graph.add_pin_style(k, v)

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
