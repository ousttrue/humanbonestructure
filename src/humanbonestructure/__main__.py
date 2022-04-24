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

    parser.add_argument('model', nargs='*')
    parser.add_argument('--asset_dir')
    parser.add_argument('--create', action='store_true',
                        help='create model procedual')
    parser.add_argument('--tpose', action='store_true',
                        help='tpose')

    args = parser.parse_args()

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('pose')

    from .gui import GUI
    gui = GUI(app.loop)

    from .formats.vpd_loader import Vpd
    if args.asset_dir:
        asset_dir = pathlib.Path(args.asset_dir)
        for root, dirs, files in os.walk(asset_dir):
            for f in files:
                f = pathlib.Path(root) / f
                if f.suffix == '.vpd':
                    from .scene.scene import vpd_loader
                    vpd = vpd_loader.Vpd.load(f.read_bytes())
                    vpd.name = f.name
                    gui.pose_generator.motion_list.items.append(vpd)

    # load model
    for model in args.model:
        gui.add_model(pathlib.Path(model))

    if args.create:
        gui.create_model()

    if args.tpose:
        gui.add_tpose()

    if gui.scenes:
        scene = gui.scenes[0]
        from .formats.tpose import TPose
        gui.pose_generator.motion_list.items.insert(
            1, TPose(scene.name, scene.root))
    gui.pose_generator.motion_list.apply()

    async def connect_async(host: str, port: int):
        import asyncio
        reader, writer = await asyncio.open_connection(host, port)
        LOGGER.debug('connected')

    app.loop.create_task(connect_async('127.0.0.1', 12721))

    from pydear.backends import impl_glfw
    impl_glfw = impl_glfw.ImplGlfwInput(app.window)
    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
