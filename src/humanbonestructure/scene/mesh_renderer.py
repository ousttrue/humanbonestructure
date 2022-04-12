from typing import Optional, List
import logging
import pkgutil
import ctypes
import glm
from pydear import glo
from pydear.scene.camera import Camera
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
    def __init__(self, vertices: ctypes.Array, indices: ctypes.Array, *,
                 joints: Optional[list] = None) -> None:
        self.vertices = vertices
        self.indices = indices
        if not joints:
            joints = []
        from .node import Node
        self.joints = joints
        self.drawable: Optional[glo.Drawable] = None
        self.bone_matrices = glm.array.zeros(len(self.joints), glm.mat4)

    def render(self, camera: Camera, node):
        if not self.vertices or not self.indices:
            return

        if not self.drawable:
            # shader
            vs = pkgutil.get_data("humanbonestructure", "assets/shader.vs")
            assert vs
            fs = pkgutil.get_data("humanbonestructure", "assets/shader.fs")
            assert fs
            shader = glo.Shader.load(vs, fs)
            assert shader

            # props
            model = glo.UniformLocation.create(shader.program, "uModel")
            view = glo.UniformLocation.create(shader.program, "uView")
            projection = glo.UniformLocation.create(
                shader.program, "uProjection")
            bone_matrices = glo.UniformLocation.create(
                shader.program, "uBoneMatrices")
            props = [
                glo.ShaderProp(
                    lambda x: model.set_mat4(x),
                    lambda:glm.value_ptr(node.world_matrix)),
                glo.ShaderProp(
                    lambda x: view.set_mat4(x),
                    lambda:glm.value_ptr(camera.view.matrix)),
                glo.ShaderProp(
                    lambda x: projection.set_mat4(x),
                    lambda:glm.value_ptr(camera.projection.matrix)),
                glo.ShaderProp(
                    lambda x: bone_matrices.set_mat4(
                        x, count=len(self.joints)),
                    lambda: self.bone_matrices.ptr),
            ]

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
        pass
        for i, joint in enumerate(self.joints):
            self.bone_matrices[i] = joint.skinning_matrix

        if self.drawable:
            self.drawable.draw()
