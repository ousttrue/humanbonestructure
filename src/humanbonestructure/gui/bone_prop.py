import logging
import glm
from pydear import imgui as ImGui
from ..scene.scene import Scene

LOGGER = logging.getLogger(__name__)


class BoneProp:
    def __init__(self, name: str, scene: Scene) -> None:
        self.name = name
        self.scene = scene

    def show(self, p_open):
        if not p_open[0]:
            return

        if ImGui.Begin(self.name, p_open):
            selected = self.scene.selected
            if selected:
                ImGui.TextUnformatted(selected.name)
                humanoid_bone = selected.humanoid_bone
                if humanoid_bone:
                    ImGui.TextUnformatted(humanoid_bone.name)
                    if ImGui.Button('force tpose'):
                        assert selected.humanoid_tail
                        dir = humanoid_bone.get_world_axis()
                        from ..formats import tpose
                        tpose.force_axis(
                            selected, selected.humanoid_tail, glm.vec3(*dir))

                    if ImGui.Button('force tpose(recursive)'):
                        for node, _ in selected.traverse_node_and_parent():
                            if node.humanoid_bone and node.humanoid_tail:
                                dir = node.humanoid_bone.get_world_axis()
                                from ..formats import tpose
                                tpose.force_axis(
                                    node, node.humanoid_tail, glm.vec3(*dir))

        ImGui.End()
