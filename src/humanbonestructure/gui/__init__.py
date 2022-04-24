from typing import List, Optional
import logging
import asyncio
import pathlib
import ctypes
from pydear import imgui as ImGui
from pydear.utils import dockspace
from ..scene.scene import Scene
from .selector import TableSelector
from .bone_mask import BoneMask
from .motion_list import MotionList, Motion
from ..eventproperty import EventProperty
from ..formats.pose import Pose

LOGGER = logging.getLogger(__name__)


class PoseGenerator:
    def __init__(self) -> None:
        self.bone_mask = BoneMask()
        self.motion_list = MotionList()
        self.pose_event = EventProperty(Pose('empty'))
        self.motion: Optional[Motion] = None

        def refilter():
            self.set_motion(self.motion)

        self.bone_mask.changed += refilter

    def show(self):
        self.motion_list._filter.show()
        self.bone_mask.show()

    def set_motion(self, motion: Optional[Motion]):
        self.motion = motion
        if motion:
            pose = motion.get_current_pose()
            self.set_pose(pose)
        else:
            self.set_pose(Pose('empty'))

    def set_pose(self, _pose: Pose):
        pose = Pose(_pose.name)
        pose.bones = [
            bone for bone in _pose.bones if bone.humanoid_bone and self.bone_mask.mask(bone.humanoid_bone)]
        self.pose_event.set(pose)


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.scenes: List[Scene] = []

        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        self.pose_generator = PoseGenerator()

        self.motion_selector = TableSelector(
            'pose selector', self.pose_generator.motion_list, self.pose_generator.show)

        self.motion_selector.selected += self.pose_generator.set_motion

        self.docks = [
            dockspace.Dock('pose_selector', self.motion_selector.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('log', log_handler.show,
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

    def _add_scene(self, name: str) -> Scene:
        scene = Scene(name)
        self.scenes.append(scene)

        self.pose_generator.pose_event += scene.set_pose

        tree_name = f'tree:{name}'
        from .bone_tree import BoneTree
        tree = BoneTree(tree_name, scene)
        self.views.append(dockspace.Dock(tree_name, tree.show,
                                         (ctypes.c_bool * 1)(True)))

        prop_name = f'prop:{name}'
        from .bone_prop import BoneProp
        prop = BoneProp(prop_name, scene)
        self.views.append(dockspace.Dock(
            prop_name, prop.show, (ctypes.c_bool*1)(True)))

        view_name = f'view:{name}'
        from .scene_view import SceneView
        view = SceneView(view_name, scene)
        self.views.append(dockspace.Dock(view_name, view.show,
                                         (ctypes.c_bool * 1)(True)))

        return scene

    def add_model(self, path: pathlib.Path):
        scene = self._add_scene(path.stem)
        scene.load_model(path)

    def create_model(self):
        scene = self._add_scene('generate')
        scene.create_model()

    def add_tpose(self):
        if not self.scenes:
            return

        scene = self._add_scene('tpose')
        scene.create_tpose_from(self.scenes[0])
