import math
import array
import glglue
import glglue.ctypesmath
from . import bvh_parser
from typing import List, NamedTuple, Iterator, Optional
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


class Bone(NamedTuple):
    offset: bvh_parser.Float3
    head: bvh_parser.Node
    tail: Optional[bvh_parser.Node] = None


class BvhSkeleton:
    def __init__(self, bvh: bvh_parser.Bvh):
        self.bvh = bvh
        self.channel_count = bvh.root.get_channel_count()
        self.bones: List[Bone] = []
        self._build(bvh.root, bvh_parser.Float3(0, 0, 0))
        self.is_initialized = False
        self.channels = []

    def _build(self, head: bvh_parser.Node, offset):
        def get_tail(node: bvh_parser.Node) -> Optional[bvh_parser.Node]:
            match len(node.children):
                case 0:
                    pass

                case 1:
                    return node.children[0]

                case _:
                    for child in node.children:
                        if child.offset.x == 0:
                            return child

        tail = get_tail(head)
        self.bones.append(Bone(offset, head, tail))
        if head.children:
            for child in head.children:
                self._build(child, offset + head.offset)

    def initialize(self):
        vertices = (bvh_parser.Float3 * len(self.bones))()
        indices = array.array('H')

        def get_index(node: bvh_parser.Node):
            for i, bone in enumerate(self.bones):
                if bone.head == node:
                    return i
            raise Exception()

        for i, bone in enumerate(self.bones):
            head = bone.offset + bone.head.offset
            vertices[i] = head
            if bone.tail:
                indices.append(i)
                indices.append(get_index(bone.tail))

        self.vbo = glglue.gl3.vbo.create_vbo_from(vertices, is_dynamic=True)
        self.ibo = glglue.gl3.vbo.create_ibo_from(indices)
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

    def _set_frame(self, it: Iterator[float], node: bvh_parser.Node, parent: glglue.ctypesmath.Mat4):
        '''
        行ベクトル。左右逆で
        '''
        offset = glglue.ctypesmath.Mat4.new_translation(
            node.offset.x, node.offset.y, node.offset.z)
        match node.channels:
            case bvh_parser.Channels.PosXYZ_RotZXY:
                t = glglue.ctypesmath.Mat4.new_translation(
                    next(it), next(it), next(it))
                z = glglue.ctypesmath.Mat4.new_rotation_z(to_radian(next(it)))
                x = glglue.ctypesmath.Mat4.new_rotation_x(to_radian(next(it)))
                y = glglue.ctypesmath.Mat4.new_rotation_y(to_radian(next(it)))
                m = y * x * z * t * offset * parent
            case bvh_parser.Channels.RotZXY:
                z = glglue.ctypesmath.Mat4.new_rotation_z(to_radian(next(it)))
                x = glglue.ctypesmath.Mat4.new_rotation_x(to_radian(next(it)))
                y = glglue.ctypesmath.Mat4.new_rotation_y(to_radian(next(it)))
                m = y * x * z * offset * parent
            case _:
                m = offset * parent

        self.matrices.append(m)
        for child in node.children:
            self._set_frame(it, child, m)

    def set_frame(self, frame: int):
        begin = self.channel_count * (frame-1)
        data = self.bvh.data[begin:begin+self.channel_count]
        self.matrices = []
        self._set_frame(iter(data), self.bvh.root,
                        glglue.ctypesmath.Mat4.new_identity())

        vertices = (bvh_parser.Float3 * len(self.matrices))()
        for i, m in enumerate(self.matrices):
            vertices[i] = bvh_parser.Float3(m._41, m._42, m._43)
        if self.vbo:
            self.vbo.update(memoryview(vertices).cast('B').tobytes())
