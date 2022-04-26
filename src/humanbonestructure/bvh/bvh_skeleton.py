import logging
import array
import ctypes
from typing import List, NamedTuple, Iterator, Optional
from OpenGL import GL
import glm
from . import bvh_parser
from pydear import glo
from pydear.scene.camera import Camera


LOGGER = logging.getLogger(__name__)

VS = """
#version 330
in vec3 aPos;
uniform mediump mat4 vp;


void main ()
{
    gl_Position = vp * vec4(aPos, 1);
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


class Bone(NamedTuple):
    offset: glm.vec3
    head: bvh_parser.Node
    tail: Optional[bvh_parser.Node] = None


class BvhSkeleton:
    def __init__(self, bvh: bvh_parser.Bvh):
        self.bvh = bvh
        self.channel_count = bvh.root.get_channel_count()
        self.bones: List[Bone] = []
        self._build(bvh.root, glm.vec3(0, 0, 0))
        self.channels = []
        # glo
        self.vertices = None
        self.drawable = None
        self.shader = None
        self.props = []

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

    def draw(self, camera: Camera):
        if not self.shader:
            # shader
            shader_or_error = glo.Shader.load(VS, FS)
            if not isinstance(shader_or_error, glo.Shader):
                LOGGER.error(shader_or_error)
                return
            self.shader = shader_or_error

            vp = glo.UniformLocation.create(self.shader.program, "vp")

            def set_vp():
                m = camera.projection.matrix * camera.view.matrix
                vp.set_mat4(glm.value_ptr(m))
            self.props.append(set_vp)

            # vertices
            self.vertices = (ctypes.c_float * (3 * len(self.bones)))()
            self.indices = array.array('H')

            def get_index(node: bvh_parser.Node):
                for i, bone in enumerate(self.bones):
                    if bone.head == node:
                        return i
                raise Exception()

            j = 0
            for i, bone in enumerate(self.bones):
                head = bone.offset + bone.head.offset
                self.vertices[j] = head.x
                j += 1
                self.vertices[j] = head.y
                j += 1
                self.vertices[j] = head.z
                j += 1
                if bone.tail:
                    self.indices.append(i)
                    self.indices.append(get_index(bone.tail))

            vbo = glo.Vbo()
            vbo.set_vertices(self.vertices, is_dynamic=True)

            ibo = glo.Ibo()
            ibo.set_indices(
                (ctypes.c_uint16 * len(self.indices))(*self.indices))

            self.drawable = glo.Vao(
                vbo, glo.VertexLayout.create_list(self.shader.program), ibo)

        assert self.drawable
        with self.shader:
            for prop in self.props:
                prop()
            self.drawable.draw(len(self.indices), topology=GL.GL_LINES)

    def _set_frame(self, it: Iterator[float], node: bvh_parser.Node, parent: glm.mat4):
        '''
        行ベクトル。左右逆で
        '''
        offset = glm.translate(node.offset)
        if node.channels:
            m = parent * offset * node.channels.get_matrix(it)
        else:
            m = parent * offset

        self.matrices.append(m)
        for child in node.children:
            self._set_frame(it, child, m)

    def set_frame(self, frame: int):
        begin = self.channel_count * (frame-1)
        data = self.bvh.data[begin:begin+self.channel_count]
        self.matrices = []
        self._set_frame(iter(data), self.bvh.root,
                        glm.mat4())

        assert self.vertices
        j = 0
        for i, m in enumerate(self.matrices):
            p = m[3].xyz
            self.vertices[j] = p.x
            j += 1
            self.vertices[j] = p.y
            j += 1
            self.vertices[j] = p.z
            j += 1
        if self.drawable:
            self.drawable.vbo.update(self.vertices)
