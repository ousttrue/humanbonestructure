from pydear.utils import dockspace
from pydear import imgui as ImGui
import asyncio
import ctypes
import pathlib
from ..scene.scene import Scene


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:

        from ..gui.pose_generator import PoseGenerator
        self.motion = PoseGenerator()

        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        self.docks = [
            dockspace.Dock('bvh', self.motion.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('logger', log_handler.show,
                           (ctypes.c_bool * 1)(True)),
        ]

        super().__init__(loop, docks=self.docks)

        self.scene = self._add_scene('bvh')
        self.motion.pose_event += self.scene.set_pose

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
        self.scene = Scene(name)
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
