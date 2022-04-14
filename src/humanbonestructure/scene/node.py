from typing import Optional
import glm
from ..formats.transform import Transform
from ..formats.humanoid_bones import HumanoidBone


def trs_matrix(t: glm.vec3, r: glm.quat, s: glm.vec3) -> glm.mat4:
    T = glm.translate(t)
    R = glm.mat4(r)
    S = glm.scale(s)
    m = T * R * S
    return m


class Node:
    def __init__(self, index: int, name: str, *,
                 position: Optional[glm.vec3] = None,
                 trs: Optional[Transform] = None) -> None:
        self.index = index
        self.name = name
        self.children = []
        self.parent = None
        self.world_matrix = glm.mat4()
        self.init_position = position
        self.init_trs = trs
        self.inverse_bind_matrix = glm.mat4()
        # renderer
        from .mesh_renderer import MeshRenderer
        self.renderer: Optional[MeshRenderer] = None
        # UI
        self.humanoid_bone: Optional[HumanoidBone] = None
        self.descendants_has_humaniod = False
        # skinning
        self.pose: Optional[Transform] = None

    def __str__(self) -> str:
        if self.init_position:
            return f'[{self.name}: {self.init_position}]'
        elif self.init_trs:
            return f'[{self.name}: {self.init_trs}]'
        else:
            raise NotImplementedError()

    @property
    def skinning_matrix(self) -> glm.mat4:
        return self.world_matrix * self.inverse_bind_matrix

    def add_child(self, child: 'Node'):
        self.children.append(child)
        child.parent = self

    def initialize(self) -> bool:
        assert self.pose is None
        if self.init_trs:
            # gltf
            pass
        elif self.init_position:
            # pmd / pmx
            if self.parent:
                t = self.init_position - self.parent.init_position
            else:
                t = self.init_position
            self.init_trs = Transform(t, glm.quat(), glm.vec3(1))
        else:
            raise NotImplementedError()

        if self.parent:
            self.world_matrix = self.parent.world_matrix * self._get_local()
        else:
            self.world_matrix = self._get_local()

        self.inverse_bind_matrix = glm.inverse(self.world_matrix)

        has = False
        if self.humanoid_bone:
            has = True

        if self.children:
            for child in self.children:
                if child.initialize():
                    self.descendants_has_humaniod = True
                    has = True
            if has:
                return True
        return False

    def _get_local(self) -> glm.mat4:
        assert self.init_trs

        if self.pose:
            t, r, s = self.init_trs
            return trs_matrix(self.pose.translation + t, self.pose.rotation * r, self.pose.scale * s)
        else:
            return trs_matrix(*self.init_trs)

    def calc_skinning(self, parent: glm.mat4):
        self.world_matrix = parent * self._get_local()
        for child in self.children:
            child.calc_skinning(self.world_matrix)
