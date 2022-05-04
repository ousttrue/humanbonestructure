from typing import Optional
import logging
import pathlib
import ctypes
from pydear import imgui as ImGui
from pydear import imgui_internal
from pydear import imnodes as ImNodes
from ...formats.bvh_parser import Bvh
from ...scene.scene import Scene
from pydear.utils.node_editor import Node, InputPin, OutputPin, NodeRuntime

LOGGER = logging.getLogger(__name__)
ASSET_DIR: Optional[pathlib.Path] = None


class BvhNodeRuntime(NodeRuntime):
    def __init__(self) -> None:
        super().__init__()
        self.bvh: Optional[Bvh] = None
        self.frame = (ctypes.c_int * 1)()

    def process(self, node: 'BvhNode'):
        if not self.bvh and node.path:
            self.load(node.path)

    def load(self, path: pathlib.Path):
        from ...formats import bvh_parser
        self.bvh = bvh_parser.from_path(path)
        if self.frame[0] >= self.bvh.frame_count:
            self.frame[0] = self.bvh.frame_count-1

    def show(self):
        if self.bvh:
            ImGui.TextUnformatted(f'bvh: {self.bvh.path.name}')
            end_frame = self.bvh.get_frame_count()-1
            for info in self.bvh.get_info():
                ImGui.TextUnformatted(info)
            ImGui.SetNextItemWidth(200)
            if ImGui.SliderInt('frame', self.frame, 0, end_frame):
                self.bvh.set_frame(self.frame[0])


class BvhSkeletonOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def process(self, node: 'BvhNode', input: InputPin):
        if node.runtime.bvh:
            input.value = node.runtime.bvh


class BvhPoseOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')

    def process(self, node: 'BvhNode', input: InputPin):
        if node.runtime.bvh:
            input.value = node.runtime.bvh.get_current_pose()


class BvhNode(Node):
    def __init__(self, get_next_id) -> None:
        super().__init__(get_next_id(), 'bvh', [], [])
        self.path: Optional[pathlib.Path] = None
        self.runtime = BvhNodeRuntime()
        # skeleton
        out_skeleton = BvhSkeletonOutputPin(get_next_id())
        self.outputs.append(out_skeleton)
        # pose
        out_pose = BvhPoseOutputPin(get_next_id())
        self.outputs.append(out_pose)

    def __str__(self):
        return f'T stance, World axis'

    def get_right_indent(self) -> int:
        return 160

    def load(self, path: pathlib.Path, graph=None):
        self.path = path
        self.runtime.load(self.path)

    def show_content(self, graph):
        if ImGui.Button('open'):
            import asyncio

            async def open_task():
                from pydear.utils import filedialog
                dir = self.path.parent if self.path else ASSET_DIR
                selected = await filedialog.open_async(asyncio.get_event_loop(), dir)
                if selected:
                    self.load(selected, graph)
            asyncio.get_event_loop().create_task(open_task())

        self.runtime.show()


class ViewNodeRuntime(NodeRuntime):
    def __init__(self) -> None:
        super().__init__()
        self.skeleton = None
        self.in_skeleton = None
        self.pose = None
        self.in_pose = None
        #
        self.scene = Scene('view')
        from pydear.scene.camera import Camera
        self.camera = Camera(distance=8, y=-0.8)
        # imgui
        self.clear_color = (ctypes.c_float * 4)(0.1, 0.2, 0.2, 1)
        self.hover_color = (ctypes.c_float * 4)(0.2, 0.3, 0.3, 1)
        from pydear import glo
        self.fbo_manager = glo.FboRenderer()
        self.bg = ImGui.ImVec4(1, 1, 1, 1)
        self.tint = ImGui.ImVec4(1, 1, 1, 1)
        self.hover = False
        self.xy = (ctypes.c_float * 2)(0, 0)

    def process(self, node: Node):
        if not self.in_skeleton:
            self.in_skeleton = next(
                iter(in_pin for in_pin in node.inputs if in_pin.name == 'skeleton'))
        if not self.in_pose:
            self.in_pose = next(
                iter(in_pin for in_pin in node.inputs if in_pin.name == 'pose'))

        if self.in_skeleton.value != self.skeleton:
            # update skeleton
            self.skeleton = self.in_skeleton.value
            self.scene.load(self.skeleton)

        if self.in_skeleton.value != self.skeleton or self.in_pose.value != self.pose:
            # update pose
            self.pose = self.in_pose.value
            self.scene.set_pose(self.in_pose.value)

    def show(self, node_id: int):
        w = 400
        h = 400
        self.camera.projection.resize(w, h)

        texture = self.fbo_manager.clear(
            w, h, self.hover_color if self.hover else self.clear_color)

        if texture:
            # x, y = ImGui.GetCursorPos()
            ImGui.ImageButton(texture, (w, h), (0, 1),
                              (1, 0), 0, self.bg, self.tint)
            imgui_internal.ButtonBehavior(ImGui.Custom_GetLastItemRect(), ImGui.Custom_GetLastItemId(), None, None,
                                          ImGui.ImGuiButtonFlags_.MouseButtonMiddle | ImGui.ImGuiButtonFlags_.MouseButtonRight)

            io = ImGui.GetIO()
            x, y = ImNodes.GetNodeScreenSpacePos(node_id)
            y += 43
            x += 8
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

            ImGui.Checkbox('skeleton', self.scene.visible_skeleton)
            ImGui.SameLine()
            ImGui.Checkbox('gizmo', self.scene.visible_gizmo)
            ImGui.SameLine()
            ImGui.Checkbox('mesh', self.scene.visible_mesh)

            # ImGui.TextUnformatted(
            #     f'{int(io.MousePos.x-x)}/{w}, {int(io.MousePos.y-y)}/{h}')


class ViewNode(Node):
    def __init__(self, get_next_id) -> None:
        super().__init__(get_next_id(), 'view',
                         [InputPin(get_next_id(), 'skeleton'),
                          InputPin(get_next_id(), 'pose')],
                         [])
        self.runtime = ViewNodeRuntime()

    def show_content(self, graph):
        self.runtime.show(self.id)
