from pydear import imgui as ImGui
from ..scene.scene import Scene
from ..scene.node import Node


def make_color(r, g, b, a):
    return r + (g << 8) + (b << 16) + (a << 24)


IM_WHITE = make_color(255, 255, 255, 255)
IM_GRAY = make_color(120, 120, 120, 120)


class BoneTree:
    def __init__(self, name: str, scene: Scene) -> None:
        self.name = name
        self.scene = scene

    def show(self, p_open):
        ImGui.SetNextWindowSize((100, 100), ImGui.ImGuiCond_.Once)
        if ImGui.Begin(self.name, p_open):
            ImGui.Checkbox('skeleton', self.scene.visible_skeleton)
            ImGui.SameLine()
            ImGui.Checkbox('gizmo', self.scene.visible_gizmo)
            ImGui.SameLine()
            ImGui.Checkbox('mesh', self.scene.visible_mesh)

            # tree
            flags = (
                ImGui.ImGuiTableFlags_.BordersV
                | ImGui.ImGuiTableFlags_.BordersOuterH
                | ImGui.ImGuiTableFlags_.Resizable
                | ImGui.ImGuiTableFlags_.RowBg
                | ImGui.ImGuiTableFlags_.NoBordersInBody
            )
            header_lablels = ("name", "humanoid bone", "pose")
            if ImGui.BeginTable("jsontree_table", len(header_lablels), flags):
                # header
                for label in header_lablels:
                    ImGui.TableSetupColumn(label)
                ImGui.TableHeadersRow()

                # body
                if self.scene.root:
                    self._traverse(self.scene.root)

                ImGui.EndTable()
        ImGui.End()

    def _traverse(self, node: Node):
        flag = 0
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
            node.humanoid_bone and not node.humanoid_bone.is_tip()) else IM_GRAY
        ImGui.PushStyleColor(ImGui.ImGuiCol_.Text, color)

        # col 0
        ImGui.TableNextColumn()

        if node.descendants_has_humanoid:
            ImGui.SetNextItemOpen(True, ImGui.ImGuiCond_.Once)
        open = ImGui.TreeNodeEx(f'{node.name}##{node.index}', flag)

        # col 1
        ImGui.TableNextColumn()
        if node.humanoid_bone:
            ImGui.TextUnformatted(f'{node.humanoid_bone.value}')
        else:
            ImGui.TextUnformatted('')

        # col 2
        if node.pose:
            ImGui.TableNextColumn()
            ImGui.TextUnformatted(f'{node.pose}')

        ImGui.PopStyleColor()

        if open:
            for child in node.children:
                self._traverse(child)
            ImGui.TreePop()
