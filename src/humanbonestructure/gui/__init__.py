from typing import List, Optional, Tuple, Callable, Iterable
import logging
import asyncio
import pathlib
import ctypes
from pydear import imgui as ImGui
from pydear.utils import dockspace
from ..scene.scene import Scene
from ..formats.humanoid_bones import HumanoidBone, HumanoidBodyParts
from ..formats import vpd_loader
from ..eventproperty import EventProperty
from .selector import Selector, TableSelector, ItemList, Filter

LOGGER = logging.getLogger(__name__)


class VpdFilter(Filter[vpd_loader.Vpd]):
    def __init__(self) -> None:
        self.filter_has_trunk = (ctypes.c_bool * 1)(False)
        self.filter_has_legs = (ctypes.c_bool * 1)(False)
        self.filter_has_leftArm = (ctypes.c_bool * 1)(False)
        self.filter_has_leftFingers = (ctypes.c_bool * 1)(True)
        self.filter_has_rightArm = (ctypes.c_bool * 1)(False)
        self.filter_has_rightFingers = (ctypes.c_bool * 1)(False)
        self.filter_has_thumbnail0 = (ctypes.c_bool * 1)(True)
        super().__init__(self.filter)

    def filter(self, item: vpd_loader.Vpd):
        if self.filter_has_trunk[0] and not any(bone.humanoid_bone.get_part() == HumanoidBodyParts.Trunk for bone in item.bones if bone.humanoid_bone):
            return False
        if self.filter_has_legs[0] and not any(bone.humanoid_bone.get_part() == HumanoidBodyParts.Legs for bone in item.bones if bone.humanoid_bone):
            return False
        if self.filter_has_leftArm[0] and not any(bone.humanoid_bone.get_part() == HumanoidBodyParts.LeftArm for bone in item.bones if bone.humanoid_bone):
            return False
        if self.filter_has_leftFingers[0] and not any(bone.humanoid_bone.get_part() == HumanoidBodyParts.LeftFingers for bone in item.bones if bone.humanoid_bone):
            return False
        if self.filter_has_rightArm[0] and not any(bone.humanoid_bone.get_part() == HumanoidBodyParts.RightArm for bone in item.bones if bone.humanoid_bone):
            return False
        if self.filter_has_rightFingers[0] and not any(bone.humanoid_bone.get_part() == HumanoidBodyParts.RightFingers for bone in item.bones if bone.humanoid_bone):
            return False
        if self.filter_has_thumbnail0[0] and not any(bone.humanoid_bone == HumanoidBone.leftThumbProximal or bone.humanoid_bone == HumanoidBone.rightThumbProximal for bone in item.bones if bone.humanoid_bone):
            return False
        return True

    def show(self):
        chcked = False
        if ImGui.Checkbox("幹", self.filter_has_trunk):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("脚", self.filter_has_legs):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("左腕", self.filter_has_leftArm):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("左指", self.filter_has_leftFingers):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("右腕", self.filter_has_rightArm):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("右指", self.filter_has_rightFingers):
            chcked = True
        ImGui.SameLine()
        if ImGui.Checkbox("has thumb0", self.filter_has_thumbnail0):
            chcked = True

        if chcked:
            self.fire()


class VpdItems(ItemList[vpd_loader.Vpd]):
    def __init__(self) -> None:
        super().__init__()
        self.items.append(vpd_loader.Vpd('__empty__'))
        self._filter = VpdFilter()

        def on_filter_changed(_):
            self.apply()
        self._filter += on_filter_changed

        self.headers = [
            "name",
            "幹",
            "脚",
            "左腕",
            "左指",
            "右腕",
            "右指",
        ]

    def filter(self, item: vpd_loader.Vpd) -> bool:
        if not self._filter.value:
            return True
        return self._filter.value(item)

    def columns(self, item: vpd_loader.Vpd) -> Iterable[str]:
        yield item.name
        yield 'O' if item.get_parts(HumanoidBodyParts.Trunk) else ''
        yield 'O' if item.get_parts(HumanoidBodyParts.Legs) else ''
        yield 'O' if item.get_parts(HumanoidBodyParts.LeftArm) else ''
        yield 'O' if item.get_parts(HumanoidBodyParts.LeftFingers) else ''
        yield 'O' if item.get_parts(HumanoidBodyParts.RightArm) else ''
        yield 'O' if item.get_parts(HumanoidBodyParts.RightFingers) else ''


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
        self.vpd_items = VpdItems()
        self.vpd_selector = TableSelector(
            'pose selector', self.vpd_items, self.vpd_items._filter.show)

        def on_select(vpd: Optional[vpd_loader.Vpd]):
            for scene in self.scenes:
                scene.load_vpd(vpd, vpd_mask.value)
        self.vpd_selector.selected += on_select

        self.docks = [
            dockspace.Dock('pose_selector', self.vpd_selector.show,
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
