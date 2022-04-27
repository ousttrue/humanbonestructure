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
            node = self.scene.selected
            if node:
                ImGui.TextUnformatted(f'{node.index}: {node.name}')
                humanoid_bone = node.humanoid_bone
                if humanoid_bone:
                    ImGui.TextUnformatted(humanoid_bone.name)
                    ImGui.TextUnformatted(f'init: {node.init_trs.rotation}')
                    if node.pose:
                        ImGui.TextUnformatted(f'pose: {node.pose}')

                    if ImGui.Button('force tpose'):
                        assert node.humanoid_tail
                        dir = humanoid_bone.get_world_axis()
                        from ..formats import tpose
                        tpose.force_axis(
                            node, node.humanoid_tail, glm.vec3(*dir))

                    if ImGui.Button('force tpose(recursive)'):
                        for node, _ in node.traverse_node_and_parent():
                            if node.humanoid_bone and node.humanoid_tail:
                                dir = node.humanoid_bone.get_world_axis()
                                from ..formats import tpose
                                tpose.force_axis(
                                    node, node.humanoid_tail, glm.vec3(*dir))

        ImGui.End()
