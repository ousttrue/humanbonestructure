from typing import Optional, Dict, Type
import pathlib
import logging
from pydear import imgui as ImGui
from pydear import imnodes as ImNodes
from pydear.utils.node_editor.editor import NodeEditor
from pydear.utils.setting import BinSetting


LOGGER = logging.getLogger(__name__)


class PoseGraphEditor(NodeEditor):
    def __init__(self, *, setting: Optional[BinSetting] = None) -> None:
        super().__init__('pose_graph', setting=setting)

    def get_klass_map(self) -> Dict[str, Type]:
        map = super().get_klass_map()
        from .bvh_node import BvhNode
        map['BvhNode'] = BvhNode
        from .view_node import ViewNode
        map['ViewNode'] = ViewNode
        from .mmd_pose_node import MmdPoseNode
        map['MmdPoseNode'] = MmdPoseNode
        return map

    def on_node_editor(self):
        open_popup = False
        if (ImGui.IsWindowFocused(ImGui.ImGuiFocusedFlags_.RootAndChildWindows) and
                ImNodes.IsEditorHovered()):
            if ImGui.IsMouseClicked(1):
                open_popup = True

        ImGui.PushStyleVar_2(ImGui.ImGuiStyleVar_.WindowPadding, (8, 8))
        if not ImGui.IsAnyItemHovered() and open_popup:
            ImGui.OpenPopup("add node")

        if ImGui.BeginPopup("add node"):
            click_pos = ImGui.GetMousePosOnOpeningCurrentPopup()
            if ImGui.MenuItem("bvh"):
                from .bvh_node import BvhNode
                node = BvhNode(
                    self.graph.get_next_id(),
                    self.graph.get_next_id(),
                    self.graph.get_next_id())
                self.graph.nodes.append(node)
                ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

            if ImGui.MenuItem("vmd/vpd"):
                from .mmd_pose_node import MmdPoseNode
                node = MmdPoseNode(
                    self.graph.get_next_id(),
                    self.graph.get_next_id())
                self.graph.nodes.append(node)
                ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

            ImGui.MenuItem("----")

            if ImGui.MenuItem("view"):
                from .view_node import ViewNode
                node = ViewNode(
                    self.graph.get_next_id(),
                    self.graph.get_next_id(),
                    self.graph.get_next_id())
                self.graph.nodes.append(node)
                ImNodes.SetNodeScreenSpacePos(node.id, click_pos)

            ImGui.EndPopup()
        ImGui.PopStyleVar()
