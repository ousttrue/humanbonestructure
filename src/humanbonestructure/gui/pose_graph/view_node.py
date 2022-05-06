import ctypes
from pydear import imgui as ImGui
from pydear import imgui_internal
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, Serialized
from ...scene.scene import Scene


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
