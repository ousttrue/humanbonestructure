import logging
import pathlib
import argparse
import os
from .gui import GUI
LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()

    # ポーズ解決のためのモデル
    parser.add_argument('model')
    # ポーズリスト
    parser.add_argument('--asset_dir')

    args = parser.parse_args()

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('posestream')

    gui = GUI(app.loop, pathlib.Path(args.model))

    if args.asset_dir:
        from ..formats.vpd_loader import Vpd
        asset_dir = pathlib.Path(args.asset_dir)
        for root, dirs, files in os.walk(asset_dir):
            for f in files:
                f = pathlib.Path(root) / f

                match f.suffix:
                    case '.vpd':
                        from ..formats import vpd_loader
                        vpd = vpd_loader.Vpd.load(f.read_bytes())
                        vpd.name = f.name
                        gui.selector.pose_generator.motion_list.items.append(
                            vpd)
                    case '.vmd':
                        from ..formats import vmd_loader
                        vpd = vmd_loader.Vmd.load(f.stem, f.read_bytes())
                        vpd.name = f.name
                        gui.selector.pose_generator.motion_list.items.append(
                            vpd)
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
