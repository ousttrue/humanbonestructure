import asyncio
import pathlib
import ctypes
import glm
from pydear import imgui as ImGui
from pydear.utils import dockspace
from pydear.scene.camera import Camera


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop, font: pathlib.Path, *, setting=None) -> None:
        from ..humanoid.humanoid_skeleton import HumanoidSkeleton, HumanoidSkeletonTrunk, HumanoidSkeletonLeftArm, HumanoidSkeletonRightArm, HumanoidSkeletonLeftLeg, HumanoidSkeletonRightLeg
        trunk = HumanoidSkeletonTrunk(glm.vec3(0, 0.85, 0),
                                      0.1, 0.1, 0.2, 0.1, 0.2)
        left_leg = HumanoidSkeletonLeftLeg(glm.vec3(0.1, 0, 0),
                                           0.4, 0.35, 0.1)
        right_leg = HumanoidSkeletonRightLeg(glm.vec3(-0.1, 0, 0),
                                             0.4, 0.35, 0.1)
        left_arm = HumanoidSkeletonLeftArm(glm.vec3(0.1, 0.2, 0),
                                           0.1, 0.3, 0.3, 0.05)
        right_arm = HumanoidSkeletonRightArm(glm.vec3(-0.1, 0.2, 0),
                                             0.1, 0.3, 0.3, 0.05)
        self.skeleton = HumanoidSkeleton(
            trunk=trunk,
            left_arm=left_arm, right_arm=right_arm,
            left_leg=left_leg, right_leg=right_leg)

        from pydear.utils.fbo_view import FboView
        self.fbo = FboView()
        self.camera = Camera(distance=6, y=-0.8)
        self.camera.bind_mouse_event(self.fbo.mouse_event)

        from .pose_scene import PoseScene
        self.scene = PoseScene(self.fbo.mouse_event, self.camera, font)
        self.scene.set_skeleton(self.skeleton)

        def render(w, h):
            self.camera.projection.resize(w, h)
            input = self.fbo.mouse_event.last_input
            if input:
                self.scene.render(self.camera, input.x, input.y)
        self.fbo.render = render

        # view
        self.clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.3, 1)
        from pydear import glo
        self.fbo_manager = glo.FboRenderer()

        self.bg = ImGui.ImVec4(1, 1, 1, 1)
        self.tint = ImGui.ImVec4(1, 1, 1, 1)

        from pydear.utils.loghandler import ImGuiLogHandler
        log_handler = ImGuiLogHandler()
        log_handler.register_root(append=True)

        from ..gui.bone_tree import BoneTree, BoneTreeScene
        self.tree = BoneTree('bone_tree', BoneTreeScene(
            get_root=self.scene.get_root,
            get_selected=self.scene.get_selected,
            set_selected=self.scene.set_selected,
            show_option=self.scene.show_option
        ))

        from ..gui.tcp_listener import TcpListener
        self.tcp = TcpListener()

        self.views = [
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
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

        super().__init__(loop, docks=self.views, setting=setting)
