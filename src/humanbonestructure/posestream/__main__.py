import logging
import pathlib
import argparse
import os
import ctypes
import asyncio
from pydear import imgui as ImGui
from pydear.utils import dockspace
from ..formats.pose import Pose
LOGGER = logging.getLogger(__name__)


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        from .tcp_listener import TcpListener
        self.tcp_listener = TcpListener()

        from .motion_selector import MotionSelector
        self.selector = MotionSelector()

        self.selector.pose_generator.pose_event += self._on_pose

        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        from .view import View
        view = View()

        self.docks = [
            dockspace.Dock('pose_selector', self.selector.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('tcp_listener', self.tcp_listener.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('view', view.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('logger', log_handler.show,
                           (ctypes.c_bool * 1)(True)),
        ]

        super().__init__(loop, docks=self.docks)

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

    def _on_pose(self, pose: Pose):
        data = pose.to_json()
        import json
        bin = json.dumps(data)
        self.tcp_listener.send(bin.encode('utf-8'))


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('model', nargs='*')
    parser.add_argument('--asset_dir')

    args = parser.parse_args()

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('posestream')

    gui = GUI(app.loop)

    if args.asset_dir:
        from ..formats.vpd_loader import Vpd
        asset_dir = pathlib.Path(args.asset_dir)
        for root, dirs, files in os.walk(asset_dir):
            for f in files:
                f = pathlib.Path(root) / f
                if f.suffix == '.vpd':
                    from ..scene.scene import vpd_loader
                    vpd = vpd_loader.Vpd.load(f.read_bytes())
                    vpd.name = f.name
                    gui.selector.pose_generator.motion_list.items.append(vpd)
    gui.selector.pose_generator.motion_list.apply()

    gui.tcp_listener.start(app.loop)

    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
