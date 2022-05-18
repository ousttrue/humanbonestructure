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


class SkeletonView:
    def __init__(self) -> None:
        from ..humanoid.humanoid_skeleton import HumanoidSkeleton
        self.property = EventProperty[HumanoidSkeleton](HumanoidSkeleton.create_default())

    def show(self, p_open):
        if p_open and not p_open[0]:
            return

        if ImGui.Begin('skeleton'):
            pass
        ImGui.End()


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop, font: pathlib.Path, *, setting=None) -> None:

        # view
        from pydear.utils.fbo_view import FboView
        self.fbo = FboView()

        # skeleton
        self.skeleton = SkeletonView()

        # scene
        from .pose_scene import PoseScene
        self.pose_scene = PoseScene(self.fbo.mouse_event, font)
        self.skeleton.property += self.pose_scene.set_skeleton
        self.pose_scene.set_skeleton(self.skeleton.property.value)
        self.fbo.render = self.pose_scene.render

        # bone tree
        from ..gui.bone_tree import BoneTree, BoneTreeScene
        self.tree = BoneTree('bone_tree', BoneTreeScene(
            get_root=self.pose_scene.get_root,
            get_selected=self.pose_scene.get_selected,
            set_selected=self.pose_scene.set_selected,
            show_option=self.pose_scene.show_option
        ))

        # tcp listener
        from ..gui.tcp_listener import TcpListener
        self.tcp = TcpListener()

        def on_pose(pose: Pose):
            self.tcp.send_data(pose.to_json())

        self.pose_scene.pose_changed += on_pose

        # logger
        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        self.views = [
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('skeleton', self.skeleton.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('view', self.fbo.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('tree', self.tree.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('tcp', self.tcp.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('logger', log_handler.show,
                           (ctypes.c_bool * 1)(True)),
        ]

        def on_menu():
            if ImGui.BeginMenu(b"Pose", True):
                if ImGui.MenuItem_2('clear', b'', None, True):
                    self.pose_scene.clear_pose()
                ImGui.EndMenu()

        super().__init__(loop, docks=self.views, setting=setting, menu=on_menu)
