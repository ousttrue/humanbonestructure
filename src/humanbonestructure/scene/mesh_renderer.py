from typing import Optional, List, Tuple
import logging
import ctypes
from OpenGL import GL
import glm
from pydear import glo
from pydear.scene.camera import Camera
from .node import Node
from ..formats.buffer_types import Float4, UShort4, Float3
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
                 joints: Optional[list] = None, flip=False) -> None:
        self.shader = ("humanbonestructure", shader)
        self.vertices = vertices
        self.indices = indices
        if flip:
            for i in range(0, len(self.indices), 3):
                i0, i1, i2 = self.indices[i:i+3]
                self.indices[i+0] = i0
                self.indices[i+1] = i2
                self.indices[i+2] = i1
        if not joints:
            joints = []
        self.joints = joints
        self.drawable: Optional[glo.Drawable] = None
        self.bone_matrices = glm.array.zeros(len(self.joints), glm.mat4)

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
                    self.bone_matrices.ptr, count=len(self.joints))

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

        # cpu skinning
        # if self.skinning_info and self.joints:
        #     for info, v in zip(self.skinning_info, self.vertices):

        #         mat_sum = glm.mat4(0)

        #         if info.weight4.x > 0:
        #             node = self.joints[info.bone4.x]
        #             mat = node.skinning_matrix
        #             mat_sum += mat * info.weight4.x
        #         if info.weight4.y > 0:
        #             node = self.joints[info.bone4.y]
        #             mat = node.skinning_matrix
        #             mat_sum += mat * info.weight4.y
        #         if info.weight4.z > 0:
        #             node = self.joints[info.bone4.z]
        #             mat = node.skinning_matrix
        #             mat_sum += mat * info.weight4.z
        #         if info.weight4.w > 0:
        #             node = self.joints[info.bone4.w]
        #             mat = node.skinning_matrix
        #             mat_sum += mat * info.weight4.w

        #         p = info.position
        #         dst = mat_sum * glm.vec3(p.x, p.y, p.z)
        #         v.position.x = dst.x
        #         v.position.y = dst.y
        #         v.position.z = dst.z

        #     self.drawable.vao.vbo.set_vertices(self.vertices)

        # gpu skinning
        for i, joint in enumerate(self.joints):
            self.bone_matrices[i] = joint.skinning_matrix

        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        if self.drawable:
            self.drawable.draw()
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
