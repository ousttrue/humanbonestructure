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
        from ..humanoid.humanoid_skeleton import (HumanoidSkeleton, HumanoidSkeletonTrunk,
                                                  HumanoidSkeletonLeftArm, HumanoidSkeletonRightArm,
                                                  HumanoidSkeletonLeftLeg, HumanoidSkeletonRightLeg,
                                                  HumanoidSkeletonLeftToes, HumanoidSkeletonRightToes,
                                                  HumanoidSkeletonFingers)
        trunk = HumanoidSkeletonTrunk(glm.vec3(0, 0.85, 0),
                                      0.1, 0.1, 0.2, 0.1, 0.2)
        left_leg = HumanoidSkeletonLeftLeg(glm.vec3(0.1, 0, 0),
                                           0.4, 0.35, 0.08)
        right_leg = HumanoidSkeletonRightLeg(glm.vec3(-0.1, 0, 0),
                                             0.4, 0.35, 0.08)
        left_arm = HumanoidSkeletonLeftArm(glm.vec3(0.1, 0.2, 0),
                                           0.1, 0.3, 0.3, 0.05)
        right_arm = HumanoidSkeletonRightArm(glm.vec3(-0.1, 0.2, 0),
                                             0.1, 0.3, 0.3, 0.05)
        left_toes = HumanoidSkeletonLeftToes(glm.vec3(0, -0.1, 0.08), 0.05)
        right_toes = HumanoidSkeletonRightToes(glm.vec3(0, -0.1, 0.08), 0.05)
        self.property = EventProperty[HumanoidSkeleton](
            HumanoidSkeleton(
                trunk=trunk,
                left_arm=left_arm, right_arm=right_arm,
                left_leg=left_leg, right_leg=right_leg,
                left_toes=left_toes, right_toes=right_toes))

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
