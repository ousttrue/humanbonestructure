from pydear import imgui as ImGui
from pydear import imnodes as ImNodes


class PoseGraph:
    def __init__(self) -> None:
        self.is_initialized = False

    def __del__(self):
        if self.is_initialized:
            ImNodes.DestroyContext()
            self.is_initialized = False

    def show(self, p_open):
        if not p_open[0]:
            return

        if ImGui.Begin("simple node editor", p_open):
            if not self.is_initialized:
                ImNodes.CreateContext()
                self.is_initialized = True

            ImNodes.BeginNodeEditor()
            ImNodes.BeginNode(1)

            ImNodes.BeginNodeTitleBar()
            ImGui.TextUnformatted("simple node :)")
            ImNodes.EndNodeTitleBar()

            ImNodes.BeginInputAttribute(2)
            ImGui.Text("input")
            ImNodes.EndInputAttribute()

            ImNodes.BeginOutputAttribute(3)
            ImGui.Indent(40)
            ImGui.Text("output")
            ImNodes.EndOutputAttribute()

            ImNodes.EndNode()
            ImNodes.EndNodeEditor()

        ImGui.End()
