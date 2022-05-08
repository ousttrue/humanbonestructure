from typing import List
import logging
import asyncio
import pathlib
import ctypes
from pydear import imgui as ImGui
from pydear.utils import dockspace
from ..scene.scene import Scene

LOGGER = logging.getLogger(__name__)


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.scenes: List[Scene] = []

        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        from ..gui.pose_receiver import PoseReceiver
        self.receiver = PoseReceiver()

        self.docks = [
            dockspace.Dock('log', log_handler.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('receiver', self.receiver.show,
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

    def _add_scene(self, name: str) -> Scene:
        scene = Scene(name)
        self.scenes.append(scene)

        self.receiver.pose_event += scene.set_pose

        tree_name = f'tree'
        from ..gui.bone_tree import BoneTree
        tree = BoneTree(tree_name, scene)
        self.views.append(dockspace.Dock(tree_name, tree.show,
                                         (ctypes.c_bool * 1)(True)))

        prop_name = f'bone'
        from ..gui.bone_prop import BoneProp
        prop = BoneProp(prop_name, scene)
        self.views.append(dockspace.Dock(
            prop_name, prop.show, (ctypes.c_bool*1)(True)))

        view_name = f'view'
        from ..gui.scene_view import SceneView
        view = SceneView(view_name, scene)
        self.views.append(dockspace.Dock(view_name, view.show,
                                         (ctypes.c_bool * 1)(True)))

        return scene

    def add_model(self, path: pathlib.Path):
        '''
        モデルをロードし T-Pose 化する
        '''
        scene = self._add_scene(path.stem)
        scene.load_model(path)

        from ..humanoid import tpose
        tpose.make_tpose(scene.root, is_inverted_pelvis=scene.is_mmd)
        delta_map = tpose.pose_to_init(scene.root)
        tpose.local_axis_fit_world(scene.root)

    def add_tpose(self):
        '''
        論理 T-Pose
        '''
        scene = self._add_scene('tpose')
        scene.create_model()
