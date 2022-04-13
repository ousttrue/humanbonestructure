import pkgutil
from typing import Optional
import ctypes
from OpenGL import GL
import glm
from pydear import glo
from ..formats.buffer_types import Float3, Float4


class Vertex(ctypes.Structure):
    _fields_ = [
        ('position', Float3),
        ('color', Float4),
    ]


S = 0.5
WHITE = Float4(1, 1, 1, 0.8)

VERTICES = [
    # X
    Vertex(Float3(0, 0, 0), Float4(1, 0, 0, 1)),
    Vertex(Float3(S, 0, 0), Float4(1, 0, 0, 1)),
    Vertex(Float3(0, 0, 0), Float4(0.5, 0, 0, 1)),
    Vertex(Float3(-S, 0, 0), Float4(0.5, 0, 0, 1)),
    # Z
    Vertex(Float3(0, 0, 0), Float4(0, 0, 1, 1)),
    Vertex(Float3(0, 0, S), Float4(0, 0, 1, 1)),
    Vertex(Float3(0, 0, 0), Float4(0, 0, 0.5, 1)),
    Vertex(Float3(0, 0, -S), Float4(0, 0, 0.5, 1)),
    # box
    Vertex(Float3(-S, 0, -S), WHITE), Vertex(Float3(S, 0, -S), WHITE),
    Vertex(Float3(S, 0, -S), WHITE), Vertex(Float3(S, 0, S), WHITE),
    Vertex(Float3(S, 0, S), WHITE), Vertex(Float3(-S, 0, S), WHITE),
    Vertex(Float3(-S, 0, S), WHITE), Vertex(Float3(-S, 0, -S), WHITE),
    # front
    Vertex(Float3(S, 0, S+0.1), WHITE), Vertex(Float3(0, 0, S+0.1+S), WHITE),
    Vertex(Float3(0, 0, S+0.1+S), WHITE), Vertex(Float3(-S, 0, S+0.1), WHITE),
    Vertex(Float3(-S, 0, S+0.1), WHITE), Vertex(Float3(S, 0, S+0.1), WHITE),
]


class Axis:
    def __init__(self) -> None:
        self.drawable: Optional[glo.Drawable] = None

    def render(self, camera):
        if not self.drawable:
            # shader
            shader = glo.Shader.load_from_pkg("humanbonestructure", "assets/line")
            assert shader

            # props
            props = shader.create_props(camera)

            vbo = glo.Vbo()

            vertices = (Vertex * len(VERTICES))(*VERTICES)
            vbo.set_vertices(vertices)
            vao = glo.Vao(vbo, glo.VertexLayout.create_list(shader.program))

            self.drawable = glo.Drawable(vao)
            self.drawable.push_submesh(shader, len(
                VERTICES), props, topology=GL.GL_LINES)

        self.drawable.draw()
