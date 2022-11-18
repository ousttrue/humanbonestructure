from typing import Optional
import logging
import ctypes
from OpenGL import GL
import glm
from pydear import glo
from pydear.scene.camera import Camera
from formats.node import Node
from formats.buffer_types import Float4, UShort4, Float3
LOGGER = logging.getLogger(__name__)


class SkinningInfo(ctypes.Structure):
    _fields_ = [
        # original position
        ('position', Float3),
        # target bones
        ('bone4', UShort4),
        # target weights
        ('weight4',  Float4),
    ]


class MeshRenderer:
    def __init__(self, shader: str, vertices: ctypes.Array, indices: ctypes.Array, *,
                 joints: Optional[list] = None) -> None:
        self.shader = ("humanbonestructure", shader)
        self.vertices = vertices
        self.indices = indices
        if not joints:
            joints = []
        self.joints = joints
        self.drawable: Optional[glo.Drawable] = None
        if self.joints:
            self.bone_matrices = glm.array.zeros(len(self.joints), glm.mat4)
        else:
            self.bone_matrices = glm.array.zeros(1, glm.mat4)

    def render(self, camera: Camera, node: Optional[Node] = None):
        if not self.vertices or not self.indices:
            return

        if not self.drawable:
            # shader
            shader = glo.Shader.load_from_pkg(*self.shader)
            assert isinstance(shader, glo.Shader)

            # props
            props = shader.create_props(camera, node)

            bone_matrices = glo.UniformLocation.create(
                shader.program, "uBoneMatrices")

            def update_bone_matrices():
                bone_matrices.set_mat4(
                    self.bone_matrices.ptr, count=len(self.bone_matrices))

            props.append(update_bone_matrices)

            # vao
            vbo = glo.Vbo()
            vbo.set_vertices(self.vertices, is_dynamic=True)

            ibo = glo.Ibo()
            ibo.set_indices(self.indices)

            vao = glo.Vao(
                vbo, glo.VertexLayout.create_list(shader.program), ibo)

            self.drawable = glo.Drawable(vao)
            self.drawable.push_submesh(shader, len(self.indices), props)

        # gpu skinning
        if self.joints:
            for i, joint in enumerate(self.joints):
                self.bone_matrices[i] = joint.skinning_matrix
        else:
            self.bone_matrices[0] = glm.mat4()

        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        if self.drawable:
            self.drawable.draw()
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
