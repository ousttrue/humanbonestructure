from typing import Optional
import logging
import pathlib
import ctypes
from pydear import imgui as ImGui
from pydear import imgui_internal
from pydear import imnodes as ImNodes
from ...formats.bvh.bvh_parser import Bvh
from ...scene.scene import Scene
from pydear.utils.node_editor.node import Node, InputPin, OutputPin, Serialized

LOGGER = logging.getLogger(__name__)
ASSET_DIR: Optional[pathlib.Path] = None


class BvhSkeletonOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')

    def process(self, node: 'BvhNode', input: InputPin):
        if node.bvh:
            input.value = node.bvh


class BvhPoseOutputPin(OutputPin):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')

    def process(self, node: 'BvhNode', input: InputPin):
        if node.bvh:
            input.value = node.bvh.get_current_pose()


class BvhNode(Node):
    def __init__(self, id: int, skeleton_pin_id: int, pose_pin_id: int, path: Optional[pathlib.Path] = None) -> None:
        super().__init__(id, 'bvh', [], [])
        if isinstance(path, str):
            path = pathlib.Path(path)
        self.path: Optional[pathlib.Path] = path
        # skeleton
        out_skeleton = BvhSkeletonOutputPin(skeleton_pin_id)
        self.outputs.append(out_skeleton)
        # pose
        out_pose = BvhPoseOutputPin(pose_pin_id)
        self.outputs.append(out_pose)

        self.bvh: Optional[Bvh] = None
        self.frame = (ctypes.c_int * 1)()

    def to_json(self) -> Serialized:
        return Serialized('BvhNode', {
            'id': self.id,
            'path': str(self.path) if self.path else None,
            'skeleton_pin_id': self.outputs[0].id,
            'pose_pin_id': self.outputs[1].id,
        })

    def __str__(self):
        return f'T stance, World axis'

    def get_right_indent(self) -> int:
        return 160

    def load(self, path: pathlib.Path):
        self.path = path
        from ...formats.bvh import bvh_parser
        self.bvh = bvh_parser.from_path(path)
        if self.frame[0] >= self.bvh.frame_count:
            self.frame[0] = self.bvh.frame_count-1

    def show_content(self, graph):
        if ImGui.Button('open'):
            import asyncio

            async def open_task():
                from pydear.utils import filedialog
                dir = self.path.parent if self.path else ASSET_DIR
                selected = await filedialog.open_async(asyncio.get_event_loop(), dir)
                if selected:
                    self.load(selected)
            asyncio.get_event_loop().create_task(open_task())

        if self.bvh:
            ImGui.TextUnformatted(f'bvh: {self.bvh.path.name}')
            end_frame = self.bvh.get_frame_count()-1
            for info in self.bvh.get_info():
                ImGui.TextUnformatted(info)
            ImGui.SetNextItemWidth(200)
            if ImGui.SliderInt('frame', self.frame, 0, end_frame):
                self.bvh.set_frame(self.frame[0])

    def process_self(self):
        if not self.bvh and self.path:
            self.load(self.path)


class ViewNode(Node):
    def __init__(self, id: int, skeleton_pin_id: int, pose_pin_id: int) -> None:
        super().__init__(id, 'view',
                         [InputPin(skeleton_pin_id, 'skeleton'),
                          InputPin(pose_pin_id, 'pose')],
                         [])

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

    def to_json(self) -> Serialized:
        return Serialized('ViewNode', {
            'id': self.id,
            'skeleton_pin_id': self.inputs[0].id,
            'pose_pin_id': self.inputs[1].id
        })

    def show_content(self, graph):
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
            x, y = ImNodes.GetNodeScreenSpacePos(self.id)
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

    def process_self(self):
        if not self.in_skeleton:
            self.in_skeleton = next(
                iter(in_pin for in_pin in self.inputs if in_pin.name == 'skeleton'))
        if not self.in_pose:
            self.in_pose = next(
                iter(in_pin for in_pin in self.inputs if in_pin.name == 'pose'))

        if self.in_skeleton.value != self.skeleton:
            # update skeleton
            self.skeleton = self.in_skeleton.value
            self.scene.load(self.skeleton)

        if self.in_skeleton.value != self.skeleton or self.in_pose.value != self.pose:
            # update pose
            self.pose = self.in_pose.value
            self.scene.set_pose(self.in_pose.value)
