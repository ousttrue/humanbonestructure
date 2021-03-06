import argparse
import pathlib
import logging

LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=pathlib.Path, required=True)
    parser.add_argument('--ini', type=pathlib.Path)
    parser.add_argument('--port', default=12721)
    args = parser.parse_args()

    setting = None
    if args.ini:
        from pydear.utils.setting import BinSetting
        setting = BinSetting(args.ini)

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('PoseMan', setting=setting)

    from .gui import GUI
    gui = GUI(app.loop, font=args.font, setting=setting)
    gui.tcp.start(app.loop, args.port)

    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()

    if setting:
        gui.save()
        app.save()
        setting.save()


if __name__ == '__main__':
    main()
