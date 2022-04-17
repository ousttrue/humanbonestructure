from .selector import Selector, Filter
from typing import List, Optional, Tuple, Callable
import logging
import asyncio
import pathlib
import ctypes
from pydear import imgui as ImGui
from pydear.utils import dockspace
from ..scene.scene import Scene
from ..formats.humanoid_bones import HumanoidBone
from ..formats import vpd_loader
from .eventproperty import EventProperty

LOGGER = logging.getLogger(__name__)


class VpdFilter(Filter[vpd_loader.Vpd]):
    def __init__(self) -> None:
        self.filter_has_lefthand = (ctypes.c_bool * 1)(True)
        self.filter_has_thumbnail0 = (ctypes.c_bool * 1)(True)
        super().__init__()

    def show(self):
        chcked = False
        if ImGui.Checkbox("leftHand", self.filter_has_lefthand):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("has thumb0", self.filter_has_thumbnail0):
            chcked = True

        if chcked:
            def on_checked(item: vpd_loader.Vpd):
                if self.filter_has_lefthand[0] and not any(bone.humanoid_bone.value.startswith('left') for bone in item.bones if bone.humanoid_bone):
                    return False
                if self.filter_has_thumbnail0[0] and not any(bone.humanoid_bone == HumanoidBone.leftThumbProximal or bone.humanoid_bone == HumanoidBone.rightThumbProximal for bone in item.bones if bone.humanoid_bone):
                    return False
                return True

            self.set(on_checked)


class VpdMask(EventProperty):
    def __init__(self) -> None:
        super().__init__(default_value=lambda x: True)
        self.use_except_finger = (ctypes.c_bool * 1)(False)
        self.use_finger = (ctypes.c_bool * 1)(True)

    def show(self):
        ImGui.Checkbox("mask except finger", self.use_except_finger)
        ImGui.SameLine()
        ImGui.Checkbox("mask finger", self.use_finger)
        if self.use_except_finger[0] and self.use_finger[0]:
            self.set(lambda x: True)
        elif self.use_except_finger[0]:
            self.set(lambda x: not x.is_finger())
        elif self.use_finger[0]:
            self.set(lambda x: x.is_finger())
        else:
            self.set(lambda x: False)


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.scenes: List[Scene] = []

        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        vpd_mask = VpdMask()
        vpd_filter = VpdFilter()

        def on_select(vpd: Optional[vpd_loader.Vpd]):
            for scene in self.scenes:
                scene.load_vpd(vpd, vpd_mask.value)
        self.selector = Selector('pose selector', vpd_filter)

        self.selector.selected += on_select

        self.docks = [
            dockspace.Dock('pose_selector', self.selector.show,
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
        scene = Scene()
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
        scene = Scene()
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

        scene = Scene()
        scene.create_tpose_from(self.scenes[0])
        self.scenes.append(scene)

        view_name = f'tpose'
        from .scene_view import SceneView
        view = SceneView(view_name, scene)
        self.views.append(dockspace.Dock(view_name, view.show,
                                         (ctypes.c_bool * 1)(True)))
