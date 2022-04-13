import pkgutil
from typing import Optional
from OpenGL import GL
import glm
from pydear.scene.camera import Camera
from pydear import glo
from .node import Node
from .axis import Vertex
from ..formats.buffer_types import Float3, Float4

S = 0.02
WHITE = Float4(1, 1, 1, 0.8)

VERTICES = [
    # X
    Vertex(Float3(0, 0, 0), Float4(1, 0, 0, 1)),
    Vertex(Float3(S, 0, 0), Float4(1, 0, 0, 1)),
    Vertex(Float3(0, 0, 0), Float4(0.5, 0, 0, 1)),
    Vertex(Float3(-S, 0, 0), Float4(0.5, 0, 0, 1)),
    # Y
    Vertex(Float3(0, 0, 0), Float4(0, 1, 0, 1)),
    Vertex(Float3(0, S, 0), Float4(0, 1, 0, 1)),
    Vertex(Float3(0, 0, 0), Float4(0, 0.5, 0, 1)),
    Vertex(Float3(0, -S, 0), Float4(0, 0.5, 0, 1)),
    # Z
    Vertex(Float3(0, 0, 0), Float4(0, 0, 1, 1)),
    Vertex(Float3(0, 0, S), Float4(0, 0, 1, 1)),
    Vertex(Float3(0, 0, 0), Float4(0, 0, 0.5, 1)),
    Vertex(Float3(0, 0, -S), Float4(0, 0, 0.5, 1)),
]


def create_local_axis(camera: Camera, node: Node):

    # shader
    vs = pkgutil.get_data("humanbonestructure", "assets/line.vs")
    assert vs
    fs = pkgutil.get_data("humanbonestructure", "assets/line.fs")
    assert fs
    shader = glo.Shader.load(vs, fs)
    assert shader

    # props
    model = glo.UniformLocation.create(shader.program, "uModel")
    view = glo.UniformLocation.create(shader.program, "uView")
    projection = glo.UniformLocation.create(
        shader.program, "uProjection")
    props = [
        glo.ShaderProp(
            lambda x: model.set_mat4(x),
            lambda: glm.value_ptr(node.world_matrix),
        ),
        glo.ShaderProp(
            lambda x: view.set_mat4(x),
            lambda:glm.value_ptr(camera.view.matrix)),
        glo.ShaderProp(
            lambda x: projection.set_mat4(x),
            lambda:glm.value_ptr(camera.projection.matrix)),
    ]

    vbo = glo.Vbo()

    vertices = (Vertex * len(VERTICES))(*VERTICES)
    vbo.set_vertices(vertices)
    vao = glo.Vao(vbo, glo.VertexLayout.create_list(shader.program))

    DRAWABLE = glo.Drawable(vao)
    DRAWABLE.push_submesh(shader, len(
        VERTICES), props, topology=GL.GL_LINES)
    return DRAWABLE
