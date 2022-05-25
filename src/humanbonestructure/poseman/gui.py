import asyncio
import logging
import pathlib
import ctypes
import glm
from pydear import imgui as ImGui
from pydear.utils import dockspace
from ..humanoid.pose import Pose
from ..eventproperty import EventProperty

LOGGER = logging.getLogger(__name__)


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop, font: pathlib.Path, *, setting=None) -> None:

        # view
        from pydear.utils.fbo_view import FboView
        self.fbo = FboView()

        # scene
        from ..scene.node_scene import NodeScene
        self.scene = NodeScene(self.fbo.mouse_event)
        from ..humanoid.bone import Skeleton
        self.scene.update(Skeleton.create_default(), None)
        self.fbo.render = self.scene.render

        # # bone tree
        # from ..gui.bone_tree import BoneTree, BoneTreeScene
        # self.tree = BoneTree('bone_tree', BoneTreeScene(
        #     get_root=self.pose_scene.get_root,
        #     get_selected=self.pose_scene.get_selected,
        #     set_selected=self.pose_scene.set_selected,
        #     show_option=self.pose_scene.show_option
        # ))

        # tcp listener
        from ..gui.tcp_listener import TcpListener
        self.tcp = TcpListener()

        def on_pose(pose: Pose):
            self.tcp.send_data(pose.to_json())

        # self.scene.pose_changed += on_pose

        # logger
        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        self.views = [
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('view', self.fbo.show,
                           (ctypes.c_bool * 1)(True)),
            # dockspace.Dock('tree', self.tree.show,
            #                (ctypes.c_bool * 1)(True)),
            dockspace.Dock('tcp', self.tcp.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('logger', log_handler.show,
                           (ctypes.c_bool * 1)(True)),
        ]

        def on_menu():
            if ImGui.BeginMenu(b"Pose", True):
                if ImGui.MenuItem_2('clear', b'', None, True):
                    self.scene.clear_pose()
                ImGui.EndMenu()

        super().__init__(loop, docks=self.views, setting=setting, menu=on_menu)
