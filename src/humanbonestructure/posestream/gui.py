import ctypes
import pathlib
import asyncio
from pydear import imgui as ImGui
from pydear.utils import dockspace
from ..formats.pose import Pose
from ..scene.scene import Scene
from ..formats import tpose


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop, model_path: pathlib.Path) -> None:
        from .tcp_listener import TcpListener
        self.tcp_listener = TcpListener()

        from .motion_selector import MotionSelector
        self.selector = MotionSelector()

        self.selector.pose_generator.pose_event += self._on_pose

        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        self.docks = [
            dockspace.Dock('pose_selector', self.selector.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('tcp_listener', self.tcp_listener.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('logger', log_handler.show,
                           (ctypes.c_bool * 1)(True)),
        ]

        super().__init__(loop, docks=self.docks)

        # load model
        scene = self._load_scene(model_path.name)
        scene.load_model(model_path)
        tpose.make_tpose(scene.root, is_inverted_pelvis=scene.is_mmd)

    def _load_scene(self, name: str) -> Scene:
        self.scene = Scene(name)
        self.selector.pose_generator.pose_event += self.scene.set_pose

        tree_name = f'tree:{name}'
        from ..gui.bone_tree import BoneTree
        tree = BoneTree(tree_name, self.scene)
        self.views.append(dockspace.Dock(tree_name, tree.show,
                                         (ctypes.c_bool * 1)(True)))

        prop_name = f'prop:{name}'
        from ..gui.bone_prop import BoneProp
        prop = BoneProp(prop_name, self.scene)
        self.views.append(dockspace.Dock(
            prop_name, prop.show, (ctypes.c_bool*1)(True)))

        view_name = f'view:{name}'
        from ..gui.scene_view import SceneView
        view = SceneView(view_name, self.scene)
        self.views.append(dockspace.Dock(view_name, view.show,
                                         (ctypes.c_bool * 1)(True)))
        return self.scene

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
        data = pose.to_json(self.scene.root)
        import json
        bin = json.dumps(data)
        self.tcp_listener.send(bin.encode('utf-8'))
