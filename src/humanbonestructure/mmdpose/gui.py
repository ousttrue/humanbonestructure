import ctypes
import pathlib
import asyncio
from pydear import imgui as ImGui
from pydear.utils import dockspace
from ..scene.scene import Scene


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop, model_path: pathlib.Path) -> None:
        from .tcp_listener import TcpListener
        self.tcp_listener = TcpListener()

        from .motion_selector import MotionSelector
        self.selector = MotionSelector()

        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        self.docks = [
            dockspace.Dock('pose_selector', self.selector.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('pose_prop', self.selector.show_selected,
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
        scene = self._add_scene(model_path.name)
        scene.load_model(model_path)

        # create tpose
        t_scene = self._add_scene('tpose')
        if False:
            t_scene.root = scene.root.copy_tree()
            from ..formats import tpose
            tpose.make_tpose(t_scene.root)
            tpose.pose_to_init(t_scene.root)
            t_scene._setup_model()
        else:
            t_scene.create_model()

        # pose event
        def _on_pose(pose):
            t_scene.set_pose(pose)

            data = pose.to_json()
            import json
            bin = json.dumps(data)
            self.tcp_listener.send(bin.encode('utf-8'))

        self.selector.pose_generator.pose_event += scene.set_pose
        scene.pose_changed += _on_pose

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
