from typing import Any, Optional, TypeAlias, Union, get_args
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, Serialized, OutputPin
from ...scene.scene import Scene
from ...humanoid.pose import Pose
from ...humanoid.humanoid_skeleton import HumanoidSkeleton


class SkeletonInputPin(InputPin[Optional[HumanoidSkeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')
        self.skeleton: Optional[HumanoidSkeleton] = None

    def set_value(self, skeleton: Optional[HumanoidSkeleton]):
        self.skeleton = skeleton


class PoseInputPin(InputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')
        self.pose: Optional[Pose] = None

    def set_value(self, pose: Optional[Pose]):
        self.pose = pose


class ViewNode(Node):
    def __init__(self, id: int, skeleton_pin_id: int, pose_pin_id: int) -> None:
        self.in_skeleton = SkeletonInputPin(skeleton_pin_id)
        self.in_pose = PoseInputPin(pose_pin_id)
        super().__init__(id, 'view',
                         [self.in_skeleton, self.in_pose],
                         [])

        self.skeleton: Optional[HumanoidSkeleton] = None
        self.pose: Optional[Pose] = None
        # imgui
        from pydear.utils.fbo_view import FboView
        self.fbo = FboView()

        #
        self.scene = Scene('view')
        from pydear.scene.camera import Camera
        self.camera = Camera(distance=8, y=-0.8)
        self.camera.bind_mouse_event(self.fbo.mouse_event)

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("view"):
            node = ViewNode(
                graph.get_next_id(),
                graph.get_next_id(),
                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

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
        x, y = ImNodes.GetNodeScreenSpacePos(self.id)
        y += 43
        x += 8        
        self.fbo.show_fbo(x, y, w, h)

        # render mesh
        assert self.fbo.mouse_event.last_input
        self.scene.render(self.camera, self.fbo.mouse_event.last_input)

        ImGui.Checkbox('gizmo', self.scene.visible_gizmo)
        ImGui.SameLine()
        ImGui.Checkbox('mesh', self.scene.visible_mesh)

    def process_self(self):
        if self.in_skeleton.skeleton != self.skeleton:
            # update skeleton
            self.skeleton = self.in_skeleton.skeleton
            self.scene.load(self.skeleton)

        if self.in_skeleton.skeleton != self.skeleton or self.in_pose.pose != self.pose:
            # update pose
            self.pose = self.in_pose.pose
            self.scene.set_pose(self.in_pose.pose)
