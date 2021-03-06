from typing import NamedTuple, Callable, Optional
from pydear import imgui as ImGui
from ..scene.scene import Scene
from ..formats.node import Node
from ..humanoid.humanoid_bones import HumanoidBone


def make_color(r, g, b, a):
    return r + (g << 8) + (b << 16) + (a << 24)


IM_WHITE = make_color(255, 255, 255, 255)
IM_GRAY = make_color(120, 120, 120, 120)


class BoneTreeScene(NamedTuple):
    show_option: Callable[[], None]
    get_root: Callable[[], Optional[Node]]
    get_selected: Callable[[], Optional[Node]]
    set_selected: Callable[[Optional[Node]], None]


class BoneTree:
    def __init__(self, name: str, scene: BoneTreeScene) -> None:
        self.name = name
        self.scene = scene

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin(self.name, p_open):
            self.scene.show_option()

            # tree
            flags = (
                ImGui.ImGuiTableFlags_.BordersV
                | ImGui.ImGuiTableFlags_.BordersOuterH
                | ImGui.ImGuiTableFlags_.Resizable
                | ImGui.ImGuiTableFlags_.RowBg
                | ImGui.ImGuiTableFlags_.NoBordersInBody
            )
            if ImGui.BeginTable("jsontree_table", 3, flags):
                # header
                ImGui.TableSetupColumn(
                    'name')
                ImGui.TableSetupColumn(
                    'humanoid bone', ImGui.ImGuiTableColumnFlags_.WidthFixed, 24)
                ImGui.TableSetupColumn(
                    'deform', ImGui.ImGuiTableColumnFlags_.WidthFixed, 10)

                ImGui.TableHeadersRow()

                # body
                ImGui.PushStyleVar(ImGui.ImGuiStyleVar_.IndentSpacing, 12)
                root = self.scene.get_root()
                if root:
                    self._traverse(root)
                ImGui.PopStyleVar()

                ImGui.EndTable()
        ImGui.End()

    def _traverse(self, node: Node):
        flag = 0
        flag |= ImGui.ImGuiTreeNodeFlags_.OpenOnArrow
        flag |= ImGui.ImGuiTreeNodeFlags_.OpenOnDoubleClick
        # flag |= ImGui.ImGuiTreeNodeFlags_.SpanAvailWidth
        # flag |= ImGui.ImGuiTreeNodeFlags_.SpanFullWidth
        if node.children:
            # dir
            pass
        else:
            # leaf
            flag |= ImGui.ImGuiTreeNodeFlags_.Leaf
            flag |= ImGui.ImGuiTreeNodeFlags_.Bullet
            # flag |= ImGui.TREE_NODE_NO_TREE_PUSH_ON_OPEN

        ImGui.TableNextRow()

        color = IM_WHITE if (
            node.humanoid_bone and not node.humanoid_bone == HumanoidBone.endSite) else IM_GRAY
        ImGui.PushStyleColor(ImGui.ImGuiCol_.Text, color)

        # col 0
        ImGui.TableNextColumn()

        if node.descendants_has_humanoid:
            ImGui.SetNextItemOpen(True, ImGui.ImGuiCond_.Once)
        open = ImGui.TreeNodeEx(f'{node.name}##{node.index}', flag)

        # col 1
        ImGui.TableNextColumn()
        humanoid_bone = node.humanoid_bone.name if node.humanoid_bone.is_enable() else ''
        # ImGui.TextUnformatted(humanoid_bone)
        selected = ImGui.Selectable(f'{humanoid_bone}##{node.index}', node ==
                                    self.scene.get_selected(), ImGui.ImGuiSelectableFlags_.SpanAllColumns)
        if selected:
            self.scene.set_selected(node)
        elif ImGui.IsItemClicked():
            self.scene.set_selected(None)

        # col 2
        ImGui.TableNextColumn()
        ImGui.TextUnformatted(f'O' if node.has_weighted_vertices else '')

        ImGui.PopStyleColor()

        if open:
            for child in node.children:
                self._traverse(child)
            ImGui.TreePop()
