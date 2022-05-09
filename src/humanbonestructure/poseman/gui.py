import asyncio
import ctypes
import glm
from pydear import imgui as ImGui
from pydear.utils import dockspace
from pydear.utils.mouseevent import MouseEvent, MouseInput
from pydear.scene.camera import Camera


class GUI(dockspace.DockingGui):
    def __init__(self, loop: asyncio.AbstractEventLoop, *, setting=None) -> None:
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

        self.camera = Camera(distance=6, y=-0.8)

        from .pose_scene import PoseScene
        self.scene = PoseScene()
        self.scene.set_skeleton(self.skeleton)

        # view
        self.clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.3, 1)
        from pydear import glo
        self.fbo_manager = glo.FboRenderer()
        self.mouse_event = MouseEvent()

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

        self.views = [
            dockspace.Dock('metrics', ImGui.ShowMetricsWindow,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('view', self.show_view,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('tree', self.tree.show,
                           (ctypes.c_bool * 1)(True)),
            dockspace.Dock('logger', log_handler.show,
                           (ctypes.c_bool * 1)(True)),
        ]

        super().__init__(loop, docks=self.views, setting=setting)

    def show_view(self, p_open):
        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (0, 0))
        if ImGui.Begin("render target", p_open,
                       ImGui.ImGuiWindowFlags_.NoScrollbar |
                       ImGui.ImGuiWindowFlags_.NoScrollWithMouse):
            w, h = ImGui.GetContentRegionAvail()
            self.camera.projection.resize(w, h)
            texture = self.fbo_manager.clear(
                int(w), int(h), self.clear_color)
            if texture:
                ImGui.ImageButton(texture, (w, h), (0, 1),
                                  (1, 0), 0, self.bg, self.tint)
                from pydear import imgui_internal
                imgui_internal.ButtonBehavior(ImGui.Custom_GetLastItemRect(), ImGui.Custom_GetLastItemId(), None, None,  # type: ignore
                                              ImGui.ImGuiButtonFlags_.MouseButtonMiddle | ImGui.ImGuiButtonFlags_.MouseButtonRight)
                io = ImGui.GetIO()
                x, y = ImGui.GetWindowPos()
                y += ImGui.GetFrameHeight()

                if ImGui.IsItemActive():
                    self.camera.mouse_drag(
                        int(io.MousePos.x-x), int(io.MousePos.y-y),
                        int(io.MouseDelta.x), int(io.MouseDelta.y),
                        io.MouseDown[0], io.MouseDown[1], io.MouseDown[2])
                else:
                    self.camera.mouse_release(
                        int(io.MousePos.x-x), int(io.MousePos.y-y))

                self.hover = ImGui.IsItemHovered()
                if self.hover:
                    self.camera.wheel(int(io.MouseWheel))

                # render mesh
                self.scene.render(self.camera)

        ImGui.End()
        ImGui.PopStyleVar()
