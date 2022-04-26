import logging
import sys
import pathlib

LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('bvh')

    from .gui import GUI
    gui = GUI(app.loop)

    gui.scene.load_bvh(pathlib.Path(sys.argv[1]))

    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
