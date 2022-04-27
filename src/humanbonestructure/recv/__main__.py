import logging
import os
import argparse
import pathlib
LOGGER = logging.getLogger(__name__)

# TODO: vmd loader
# TODO: bvh loader
# TODO: gltf animation
# TODO: human -> node: retarget
# TODO: human bone gizmo
# TODO: trackball camera
# TODO: mediapipe
# TODO: pose -> axis angle
# TODO: camera fit to hand
# TODO: multi angle


def main():
    logging.basicConfig(level=logging.DEBUG)

    # args
    parser = argparse.ArgumentParser()
    parser.add_argument('--model')
    parser.add_argument('--tpose', action='store_true')
    parser.add_argument('--connect', action='store_true')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=12721)
    args = parser.parse_args()

    # gui
    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('pose')
    from .gui import GUI
    gui = GUI(app.loop)

    # load model
    if args.model:
        gui.add_model(pathlib.Path(args.model))
    elif args.tpose:
        gui.add_tpose()
    # connect
    if args.connect or args.host != '127.0.0.1' or args.port != 12721:
        app.loop.create_task(gui.receiver.connect_async(args.host, args.port))

    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
