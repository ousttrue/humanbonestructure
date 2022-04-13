import logging
import os
import argparse
import pathlib
LOGGER = logging.getLogger(__name__)

# TODO: pmx loader
# TODO: vmd loader
# TODO: bvh loader
# TODO: gltf animation
# TODO: human -> node: retarget
# TODO: human bone gizmo
# TODO: trackball camera
# TODO: mediapipe
# TODO: local axis
# TODO: pose -> axis angle
# TODO: camera fit to hand
# TODO: multi angle


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()

    parser.add_argument('model', nargs='+')
    parser.add_argument('--asset_dir')
    parser.add_argument('--create', action='store_true',
                        help='create model procedual')

    args = parser.parse_args()

    vpd_list = []
    if args.asset_dir:
        asset_dir = pathlib.Path(args.asset_dir)
        for root, dirs, files in os.walk(asset_dir):
            for f in files:
                f = pathlib.Path(root) / f
                if f.suffix == '.vpd':
                    from .scene.scene import vpd_loader
                    vpd = vpd_loader.Vpd(f.read_bytes())
                    vpd.name = f.name
                    vpd_list.append(vpd)

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('pose')

    from .gui import GUI
    gui = GUI(app.loop)
    gui.selector.items = vpd_list

    for model in args.model:
        gui.add_model(pathlib.Path(model))

    if args.create:
        gui.create_model()

    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
