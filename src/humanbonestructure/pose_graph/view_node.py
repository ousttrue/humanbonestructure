from typing import Optional
import ctypes
import glm
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.node import Node, InputPin, Serialized, OutputPin
from ..humanoid.pose import Pose
from ..humanoid.bone import Skeleton


class SkeletonInputPin(InputPin[Optional[Skeleton]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'skeleton')
        self.skeleton: Optional[Skeleton] = None

    def set_value(self, skeleton: Optional[Skeleton]):
        self.skeleton = skeleton


class PoseInputPin(InputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')
        self.pose: Optional[Pose] = None

    def set_value(self, pose: Optional[Pose]):
        self.pose = pose


class PoseOutputPin(OutputPin[Optional[Pose]]):
    def __init__(self, id: int) -> None:
        super().__init__(id, 'pose')

    def get_value(self, node: 'ViewNode') -> Optional[Pose]:
        return node.scene.pose_changed.value


class ViewNode(Node):
    def __init__(self, id: int, in_skeleton_id: int, in_pose_id: int, out_pose_id) -> None:
        self.in_skeleton = SkeletonInputPin(in_skeleton_id)
        self.in_pose = PoseInputPin(in_pose_id)
        self.out_pose = PoseOutputPin(out_pose_id)
        super().__init__(id, 'view',
                         [self.in_skeleton, self.in_pose],
                         [self.out_pose])

        # imgui
        from pydear.utils.fbo_view import FboView
        self.fbo = FboView()
        from ..scene.node_scene import NodeScene
        self.scene = NodeScene(self.fbo.mouse_event)
        # render mesh
        self.fbo.render = self.scene.render

        self.cancel_axis = (ctypes.c_bool * 1)()

    @classmethod
    def imgui_menu(cls, graph, click_pos):
        if ImGui.MenuItem("view"):
            node = ViewNode(
                graph.get_next_id(),
                graph.get_next_id(),
                graph.get_next_id(),
                graph.get_next_id())
            graph.nodes.append(node)
            ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

    def to_json(self) -> Serialized:
        return Serialized('ViewNode', {
            'id': self.id,
            'in_skeleton_id': self.inputs[0].id,
            'in_pose_id': self.inputs[1].id,
            'out_pose_id': self.outputs[0].id,
        })

    def get_right_indent(self) -> int:
        return 360

    def show_content(self, graph):
        w = 400
        h = 400
        x, y = ImNodes.GetNodeScreenSpacePos(self.id)
        y += 43
        x += 8
        self.fbo.show_fbo(x, y, w, h)

        if self.scene.skeleton:
            ImGui.Checkbox('cancel axis', self.cancel_axis)

            if self.cancel_axis[0]:
                if ImGui.Button("strict tpose"):
                    self.scene.skeleton.strict_tpose()
                    self.scene.sync_gizmo()
                if ImGui.Button('clear'):
                    self.scene.skeleton.clear_pose()
                    self.scene.sync_gizmo()
                # if ImGui.Button('clear pose'):
                #     self.scene.root.clear_pose()
                #     self.scene.root.calc_world_matrix(glm.mat4())
                #     self.scene.drag_handler.select(None)
                #     self.scene.sync_gizmo()
                #     self.scene.raise_pose()

    def process_self(self):
        self.scene.update(self.in_skeleton.skeleton,
                          self.in_pose.pose, self.cancel_axis[0])
