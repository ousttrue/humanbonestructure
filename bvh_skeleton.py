import math
import array
import glglue
import glglue.ctypesmath
import bvh_parser
from typing import List
from OpenGL import GL


VS = """
#version 330
in vec3 aPosition;
uniform mediump mat4 m;
uniform mediump mat4 vp;


void main ()
{
    gl_Position = vec4(aPosition, 1) * m * vp;
}
"""

FS = """
#version 330
out vec4 fColor;
void main()
{
    fColor = vec4(1, 1, 1, 1);
}
"""


def to_radian(degree):
    return degree / 180.0 * math.pi


class BvhSkeleton:
    def __init__(self, bvh: bvh_parser.Bvh, scale: float):
        self.vertices: List[bvh_parser.Float3] = []
        self._build(bvh.root, bvh_parser.Float3(0, 0, 0))
        for i, v in enumerate(self.vertices):
            self.vertices[i] = v * scale
        self.is_initialized = False

    def _build(self, head: bvh_parser.Node, offset):
        if head.children:
            if len(head.children) == 1:
                tail = head.children[0]
                self._push_bone(offset, head, tail)
                self._build(tail, offset + head.offset)
            else:
                for child in head.children:
                    if child.offset.x == 0:
                        self._push_bone(offset, head, child)
                    self._build(child, offset + head.offset)

    def _push_bone(
        self, offset: bvh_parser.Float3, head: bvh_parser.Node, tail: bvh_parser.Node
    ):
        v0 = offset + head.offset
        self.vertices.append(v0)
        v1 = v0 + tail.offset
        self.vertices.append(v1)

    def initialize(self):
        vertices = (bvh_parser.Float3 * len(self.vertices))()
        for i, v in enumerate(self.vertices):
            vertices[i] = v
        self.vbo = glglue.gl3.vbo.create_vbo_from(vertices)
        self.ibo = glglue.gl3.vbo.create_ibo_from(
            array.array('H', range(len(vertices))))
        self.ibo.topology = GL.GL_LINES
        self.shader = glglue.gl3.shader.create_from(VS, FS)
        self.is_initialized = True

    def draw(self, projection, view):
        if not self.is_initialized:
            self.initialize()
        self.shader.use()
        self.shader.uniforms["vp"].set(view * projection)

        m = glglue.ctypesmath.Mat4.new_identity()
        self.shader.uniforms["m"].set(m)
        self.vbo.set_slot(0)
        self.ibo.draw()
