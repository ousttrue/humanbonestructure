from typing import List, Optional
import logging
import asyncio
import pathlib
import ctypes
from pydear import imgui as ImGui
from pydear.utils import dockspace
from ..scene.scene import Scene
from .selector import TableSelector
from .bone_mask import VpdMask

LOGGER = logging.getLogger(__name__)


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.scenes: List[Scene] = []

        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        vpd_mask = VpdMask()
        from .motion_list import MotionList, Motion
        self.motion_list = MotionList()

        def show():
            self.motion_list._filter.show()
            vpd_mask.show()

        self.motion_selector = TableSelector(
            'pose selector', self.motion_list, show)

        def on_select(motion: Optional[Motion]):
            for scene in self.scenes:
                scene.motion = motion
                scene.mask = vpd_mask.mask
        self.motion_selector.selected += on_select

        self.docks = [
            dockspace.Dock('pose_selector', self.motion_selector.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('log', log_handler.draw,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
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

    def add_model(self, path: pathlib.Path):
        scene = Scene(path.stem)
        scene.load_model(path)
        self.scenes.append(scene)

        tree_name = f'tree:{path.name}'
        from .bone_tree import BoneTree
        tree = BoneTree(tree_name, scene)

        view_name = f'view:{path.name}'
        from .scene_view import SceneView
        view = SceneView(view_name, scene)

        self.views.append(dockspace.Dock(tree_name, tree.show,
                                         (ctypes.c_bool * 1)(True)))
        self.views.append(dockspace.Dock(view_name, view.show,
                                         (ctypes.c_bool * 1)(True)))

    def create_model(self):
        scene = Scene('generate')
        scene.create_model()
        self.scenes.append(scene)

        tree_name = f'tree:__procedual__'
        from .bone_tree import BoneTree
        tree = BoneTree(tree_name, scene)
        self.views.append(dockspace.Dock(tree_name, tree.show,
                                         (ctypes.c_bool * 1)(True)))

        view_name = f'view:__procedual__'
        from .scene_view import SceneView
        view = SceneView(view_name, scene)
        self.views.append(dockspace.Dock(view_name, view.show,
                                         (ctypes.c_bool * 1)(True)))

    def add_tpose(self):
        if not self.scenes:
            return

        scene = Scene('tpose')
        scene.create_tpose_from(self.scenes[0])
        self.scenes.append(scene)

        view_name = f'tpose'
        from .scene_view import SceneView
        view = SceneView(view_name, scene)
        self.views.append(dockspace.Dock(view_name, view.show,
                                         (ctypes.c_bool * 1)(True)))
