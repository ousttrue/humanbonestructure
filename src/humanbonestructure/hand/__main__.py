import logging
import numpy
from pydear import imgui as ImGui
from mediapipe.python.solutions import hands as mp_hands
logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    from pydear.utils.loghandler import ImGuiLogHandler
    log_handler = ImGuiLogHandler()
    log_handler.setFormatter(logging.Formatter(
        '%(name)s:%(lineno)s[%(levelname)s]%(message)s'))
    log_handler.register_root()

    from pydear.utils import glfw_app
    app = glfw_app.GlfwApp('hello_docking')

    from pydear.utils import dockspace
    import ctypes

    from ..gui.hand_landmark_table import HandLandMarkTable
    landmark_table = HandLandMarkTable()

    from ..scene.scene_capture import CaptureScene
    capture = CaptureScene()

    from ..scene.scene_3d import Scene
    scene = Scene()

    from ..scene.scene_hand import HandScene
    hand = HandScene()

    hands = mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    from ..eventproperty import EventProperty
    landmark_result: EventProperty[mp_hands.SolutionOutputs] = EventProperty()

    def estimate(image: numpy.ndarray):
        assert isinstance(image, numpy.ndarray)

        results = hands.process(image)
        landmark_result.set(results)

    from ..formats.video_capture import VideCapture
    video_capture = VideCapture()
    video_capture.frame_event += capture.rect.update_capture_texture
    video_capture.frame_event += estimate

    landmark_result += landmark_table.update
    # landmark_result += scene.update
    # landmark_result += hand.update

    views = [
        dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('landmarks', landmark_table.show,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('capture', capture.show,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('scene', scene.show,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('hand', hand.show,
                       (ctypes.c_bool * 1)(True)),
        dockspace.Dock('log', log_handler.draw, (ctypes.c_bool * 1)(True)),
    ]

    gui = dockspace.DockingGui(app.loop, docks=views)

    app.loop.create_task(video_capture.start_async())

    from pydear.backends.impl_glfw import ImplGlfwInput
    impl_glfw = ImplGlfwInput(app.window)

    while app.clear():
        impl_glfw.process_inputs()
        gui.render()
    del gui


if __name__ == '__main__':
    main()
