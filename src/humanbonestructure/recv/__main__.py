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

    parser = argparse.ArgumentParser()

    parser.add_argument('model')
    parser.add_argument('--asset_dir')
    # parser.add_argument('--create', action='store_true',
    #                     help='create model procedual')
    # parser.add_argument('--tpose', action='store_true',
    #                     help='tpose')

    args = parser.parse_args()

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('pose')

    from .gui import GUI
    gui = GUI(app.loop)

    # load model
    gui.add_model(pathlib.Path(args.model))

    # if args.create:
    #     gui.create_model()

    gui.add_tpose()

    # if gui.scenes:
    #     scene = gui.scenes[0]
    #     from .formats.tpose import TPose
    #     gui.pose_generator.motion_list.items.insert(
    #         1, TPose(scene.name, scene.root))

    app.loop.create_task(gui.receiver.connect_async('127.0.0.1', 12721))

    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
