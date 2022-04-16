from typing import Optional, List
import ctypes
from OpenGL import GL
from pydear.scene.camera import Camera
from pydear import glo
from .scene import Node
from ..formats.buffer_types import Float3, Float4


class MeshVertex(ctypes.Structure):
    _fields_ = [

    ]


class LineVertex(ctypes.Structure):
    _fields_ = [
        ('position', Float3),
        ('color', Float4),
    ]


S = 0.5
WHITE = Float4(1, 1, 1, 0.8)

# 足元の軸表示
LINE_VERTICES = [
    # X
    LineVertex(Float3(0, 0, 0), Float4(1, 0, 0, 1)),
    LineVertex(Float3(S, 0, 0), Float4(1, 0, 0, 1)),
    LineVertex(Float3(0, 0, 0), Float4(0.5, 0, 0, 1)),
    LineVertex(Float3(-S, 0, 0), Float4(0.5, 0, 0, 1)),
    # Z
    LineVertex(Float3(0, 0, 0), Float4(0, 0, 1, 1)),
    LineVertex(Float3(0, 0, S), Float4(0, 0, 1, 1)),
    LineVertex(Float3(0, 0, 0), Float4(0, 0, 0.5, 1)),
    LineVertex(Float3(0, 0, -S), Float4(0, 0, 0.5, 1)),
    # box
    LineVertex(Float3(-S, 0, -S), WHITE), LineVertex(Float3(S, 0, -S), WHITE),
    LineVertex(Float3(S, 0, -S), WHITE), LineVertex(Float3(S, 0, S), WHITE),
    LineVertex(Float3(S, 0, S), WHITE), LineVertex(Float3(-S, 0, S), WHITE),
    LineVertex(Float3(-S, 0, S), WHITE), LineVertex(Float3(-S, 0, -S), WHITE),
    # front
    LineVertex(Float3(S, 0, S+0.1),
               WHITE), LineVertex(Float3(0, 0, S+0.1+S), WHITE),
    LineVertex(Float3(0, 0, S+0.1+S),
               WHITE), LineVertex(Float3(-S, 0, S+0.1), WHITE),
    LineVertex(Float3(-S, 0, S+0.1),
               WHITE), LineVertex(Float3(S, 0, S+0.1), WHITE),
]


class LinePush:
    def __init__(self, lines, offset) -> None:
        self.offset = offset
        self.lines = lines
        self.pos = 0

    def push_line(self, begin, dir, length, color):
        self.lines[self.offset + self.pos] = LineVertex(
            Float3(
                begin.x,
                begin.y,
                begin.z),
            color)
        self.pos += 1
        self.lines[self.offset + self.pos] = LineVertex(
            Float3(
                begin.x + dir.x * length,
                begin.y + dir.y * length,
                begin.z + dir.z * length),
            color)
        self.pos += 1


class Gizmo:
    '''
    モデル一体のGizmo。Triangle と Line ２本立て

    * Axis
    * Boneのビジュアライズ

    など
    '''

    def __init__(self) -> None:
        self.lines = (LineVertex * 65535)()
        for i, p in enumerate(LINE_VERTICES):
            self.lines[i] = p
        self.lines_vbo: Optional[glo.Vbo] = None
        self.lines_vao: Optional[glo.Vao] = None
        self.lines_submeshes: List[glo.Submesh] = []
        self.lines_updated = False

        # submesh(axis)
        self.lines_submeshes.append(glo.Submesh(
            topology=GL.GL_LINES, draw_count=len(LINE_VERTICES)))
        self.lines_submeshes.append(glo.Submesh(topology=GL.GL_LINES))

    def update(self, root: Node):
        # add local axis
        push = LinePush(self.lines, len(LINE_VERTICES))

        for node, _ in root.traverse_node_and_parent():
            if node.humanoid_bone:
                m = node.world_matrix
                pos = m[3]
                push.push_line(pos, m[0], 0.02, Float4(1, 0, 0, 1))
                push.push_line(pos, m[1], 0.02, Float4(0, 1, 0, 1))
                push.push_line(pos, m[2], 0.02, Float4(0, 0, 1, 1))

        self.lines_submeshes[1].draw_count = push.pos
        self.lines_updated = True

    def init_line_drawable(self, camera: Camera) -> glo.Vao:
        if not self.lines_vao:
            # shader/props
            shader = glo.Shader.load_from_pkg(
                "humanbonestructure", "assets/line")
            assert shader
            props = shader.create_props(camera)
            for submesh in self.lines_submeshes:
                submesh.shader = shader
                submesh.properties = props

            # vbo/vao
            self.lines_vbo = glo.Vbo()
            self.lines_vbo.set_vertices(self.lines, is_dynamic=True)
            self.lines_vao = glo.Vao(
                self.lines_vbo, glo.VertexLayout.create_list(shader.program))

        elif self.lines_updated:
            assert self.lines_vbo
            self.lines_vbo.update(self.lines)

        return self.lines_vao

    def render(self, camera: Camera):
        lines_vao = self.init_line_drawable(camera)

        GL.glEnable(GL.GL_DEPTH_TEST)
        lines_vao.bind()
        offset = 0
        for submesh in self.lines_submeshes:
            assert submesh.shader
            with submesh.shader:
                for prop in submesh.properties:
                    prop()
                lines_vao.draw(submesh.draw_count, offset=offset,
                               topology=submesh.topology)
            offset += submesh.draw_count
        lines_vao.unbind()
        GL.glDisable(GL.GL_DEPTH_TEST)
