from typing import NamedTuple, Optional
import logging
import ctypes
import math
from OpenGL import GL
import glm
from pydear import glo

LOGGER = logging.getLogger(__name__)

VS = '''
#version 330
in vec3 aPosition;
in vec4 aColor;
out vec4 vColor;
uniform mediump mat4 vp;

void main() {
  gl_Position = vp * vec4(aPosition, 1);
  vColor = aColor;
}
'''

FS = '''
#version 330
in vec4 vColor;
out vec4 fColor;
void main() { fColor = vColor; }
'''


class AABB(NamedTuple):
    min: glm.vec3
    max: glm.vec3

    def __str__(self) -> str:
        return f'AABB({self.min}, {self.max})'

    def expand(self, rhs: 'AABB') -> 'AABB':
        min = self.min.copy()
        if rhs.min.x < min.x:
            min.x = rhs.min.x
        if rhs.min.y < min.y:
            min.y = rhs.min.y
        if rhs.min.z < min.z:
            min.z = rhs.min.z

        max = self.max.copy()
        if rhs.max.x > max.x:
            max.x = rhs.max.x
        if rhs.max.y > max.y:
            max.y = rhs.max.y
        if rhs.max.z > max.z:
            max.z = rhs.max.z

        return AABB(min, max)

    def transform(self, m: glm.mat4) -> 'AABB':
        p0 = (m * glm.vec4(self.min, 1)).xyz
        p1 = (m * glm.vec4(self.max, 1)).xyz
        min_x, max_x = (p0.x, p1.x) if p0.x < p1.x else (p1.x, p0.x)
        min_y, max_y = (p0.y, p1.y) if p0.y < p1.y else (p1.y, p0.y)
        min_z, max_z = (p0.z, p1.z) if p0.z < p1.z else (p1.z, p0.z)
        return AABB(glm.vec3(min_x, min_y, min_z), glm.vec3(max_x, max_y, max_z))

    @staticmethod
    def new_empty() -> 'AABB':
        return AABB(glm.vec3(float('inf'), float('inf'), float('inf')), -glm.vec3(float('inf'), float('inf'), float('inf')))


kEpsilon = 1e-5


class Ray(NamedTuple):
    origin: glm.vec3
    dir: glm.vec3

    def intersect_triangle(self, v0: glm.vec3, v1: glm.vec3, v2: glm.vec3) -> Optional[float]:
        '''
        https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/ray-triangle-intersection-geometric-solution
        '''
        # compute plane's normal
        v0v1 = v1 - v0
        v0v2 = v2 - v0
        # no need to normalize
        N = glm.cross(v0v1, v0v2)  # N
        # area2 = N.get_length()

        # Step 1: finding P

        # check if ray and plane are parallel ?
        NdotRayDirection = glm.dot(N, self.dir)
        if math.fabs(NdotRayDirection) < kEpsilon:  # almost 0
            return  # they are parallel so they don't intersect !

        # compute d parameter using equation 2
        d = -glm.dot(N, v0)

        # compute t (equation 3)
        t = -(glm.dot(N, self.origin) + d) / NdotRayDirection
        # check if the triangle is in behind the ray
        if t < 0:
            return  # the triangle is behind

        # compute the intersection point using equation 1
        P = self.origin + self.dir * t

        # Step 2: inside-outside test
        # Vec3f C  # vector perpendicular to triangle's plane

        # edge 0
        edge0 = v1 - v0
        vp0 = P - v0
        C = glm.cross(edge0, vp0)
        if glm.dot(N, C) < 0:
            return  # P is on the right side

        # edge 1
        edge1 = v2 - v1
        vp1 = P - v1
        C = glm.cross(edge1, vp1)
        if glm.dot(N, C) < 0:
            return  # P is on the right side

        # edge 2
        edge2 = v0 - v2
        vp2 = P - v2
        C = glm.cross(edge2, vp2)
        if glm.dot(N, C) < 0:
            return  # P is on the right side

        return t  # this ray hits the triangle


class Vertex(ctypes.Structure):

    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float),
        ('r', ctypes.c_float),
        ('g', ctypes.c_float),
        ('b', ctypes.c_float),
        ('a', ctypes.c_float),
    ]

    @staticmethod
    def pos_color(p: glm.vec3, c: glm.vec4) -> 'Vertex':
        return Vertex(
            p.x,
            p.y,
            p.z,
            c.r,
            c.g,
            c.b,
            c.a,
        )


class Gizmo:
    def __init__(self) -> None:
        # state
        self.viewport = glm.vec4(0, 0, 1, 1)
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_left_down = False
        self.mouse_right_down = False
        self.mouse_middle_down = False
        self.camera_view = glm.mat4()
        self.camera_projection = glm.mat4()
        self.ray = Ray(glm.vec3(0, 0, 0), glm.vec3(0, 0, 1))
        self.light = glm.vec4(1, 1, 1, 1)

        self.matrix = glm.mat4()
        self.color = glm.vec4(1, 1, 1, 1)
        # event
        self.click_left = False
        self.click_middle = False
        self.click_right = False

        self.line_shader: Optional[glo.Shader] = None
        self.line_props = []
        # lines
        self.lines = (Vertex * 65535)()
        self.line_count = 0
        self.line_drawable: Optional[glo.Vao] = None
        # triangles
        self.triangles = (Vertex * 65535)()
        self.triangle_count = 0
        self.triangle_drawable: Optional[glo.Vao] = None

        # hover selectable
        self.hover = None
        self.hover_last = None

    def begin(self, viewport, x, y,
              mouse_left_down, mouse_right_down, mouse_middle_down,
              view: glm.mat4, projection: glm.mat4, ray, light):
        # clear
        self.line_count = 0
        self.triangle_count = 0
        self.matrix = glm.mat4()
        self.color = glm.vec4(1, 1, 1, 1)
        # update
        self.click_left = self.mouse_left_down and not mouse_left_down
        self.click_right = self.mouse_right_down and not mouse_right_down
        self.click_middle = self.mouse_middle_down and not mouse_middle_down

        self.viewport = viewport
        self.mouse_x = x
        self.mouse_y = y
        self.mouse_left_down = mouse_left_down
        self.mouse_right_down = mouse_right_down
        self.mouse_middle_down = mouse_middle_down
        self.camera_view = view
        self.camera_projection = projection
        self.ray = Ray(glm.vec3(*ray.origin), glm.vec3(*ray.dir))
        self.light = light

        self.hover_last = self.hover
        self.hover = None

    def end(self):
        if not self.line_shader:
            # shader
            shader_or_error = glo.Shader.load(VS, FS)
            if not isinstance(shader_or_error, glo.Shader):
                LOGGER.error(shader_or_error)
                raise Exception()
            self.line_shader = shader_or_error

            vp = glo.UniformLocation.create(self.line_shader.program, "vp")

            def set_vp():
                m = self.camera_projection * self.camera_view
                vp.set_mat4(glm.value_ptr(m))
            self.line_props.append(set_vp)

            # lines
            line_vbo = glo.Vbo()
            line_vbo.set_vertices(self.lines, is_dynamic=True)

            self.line_drawable = glo.Vao(
                line_vbo, glo.VertexLayout.create_list(self.line_shader.program))

            # vertices
            triangle_vbo = glo.Vbo()
            triangle_vbo.set_vertices(self.lines, is_dynamic=True)

            self.triangle_drawable = glo.Vao(
                triangle_vbo, glo.VertexLayout.create_list(self.line_shader.program))

        else:
            assert self.line_drawable
            self.line_drawable.vbo.update(self.lines)

            assert self.triangle_drawable
            self.triangle_drawable.vbo.update(self.triangles)

        assert self.line_drawable
        assert self.triangle_drawable

        with self.line_shader:
            for prop in self.line_props:
                prop()

            GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
            GL.glEnable(GL.GL_BLEND)
            self.triangle_drawable.draw(
                self.triangle_count, topology=GL.GL_TRIANGLES)
            GL.glDisable(GL.GL_BLEND)
            GL.glEnable(GL.GL_DEPTH_TEST)

            self.line_drawable.draw(self.line_count, topology=GL.GL_LINES)

    def line(self, p0: glm.vec3, p1: glm.vec3):
        p0 = (self.matrix * glm.vec4(p0, 1)).xyz
        self.lines[self.line_count] = Vertex.pos_color(p0, self.color)
        self.line_count += 1

        p1 = (self.matrix * glm.vec4(p1, 1)).xyz
        self.lines[self.line_count] = Vertex.pos_color(p1, self.color)
        self.line_count += 1

    def triangle(self, p0: glm.vec3, p1: glm.vec3, p2: glm.vec3, *, intersect=False):
        p0 = (self.matrix * glm.vec4(p0, 1)).xyz
        p1 = (self.matrix * glm.vec4(p1, 1)).xyz
        p2 = (self.matrix * glm.vec4(p2, 1)).xyz

        self.triangles[self.triangle_count] = Vertex.pos_color(p0, self.color)
        self.triangle_count += 1

        self.triangles[self.triangle_count] = Vertex.pos_color(p1, self.color)
        self.triangle_count += 1

        self.triangles[self.triangle_count] = Vertex.pos_color(p2, self.color)
        self.triangle_count += 1

        if intersect:
            return self.ray.intersect_triangle(p0, p1, p2)

    def quad(self, p0: glm.vec3, p1: glm.vec3, p2: glm.vec3, p3: glm.vec3):
        self.triangle(p0, p1, p2)
        self.triangle(p2, p3, p0)

    def axis(self, size: float):
        origin = glm.vec3(0, 0, 0)
        # X
        self.color = glm.vec4(1, 0, 0, 1)
        self.line(origin, glm.vec3(size, 0, 0))
        self.color = glm.vec4(0.5, 0, 0, 1)
        self.line(origin, glm.vec3(-size, 0, 0))
        # Y
        self.color = glm.vec4(0, 1, 0, 1)
        self.line(origin, glm.vec3(0, size, 0))
        self.color = glm.vec4(0, 0.5, 0, 1)
        self.line(origin, glm.vec3(0, -size, 0))
        # Z
        self.color = glm.vec4(0, 0, 1, 1)
        self.line(origin, glm.vec3(0, 0, size))
        self.color = glm.vec4(0, 0, 0.5, 1)
        self.line(origin, glm.vec3(0, 0, -size))

    def aabb(self, aabb: AABB):
        self.color = glm.vec4(1, 1, 1, 1)
        match aabb:
            case AABB(glm.vec3(nx, ny, nz), glm.vec3(px, py, pz)):
                t0 = glm.vec3(nx, py, nz)
                t1 = glm.vec3(px, py, nz)
                t2 = glm.vec3(px, py, pz)
                t3 = glm.vec3(nx, py, pz)
                b0 = glm.vec3(nx, ny, nz)
                b1 = glm.vec3(px, ny, nz)
                b2 = glm.vec3(px, ny, pz)
                b3 = glm.vec3(nx, ny, pz)
                # top
                self.line(t0, t1)
                self.line(t1, t2)
                self.line(t2, t3)
                self.line(t3, t0)
                # bottom
                self.line(b0, b1)
                self.line(b1, b2)
                self.line(b2, b3)
                self.line(b3, b0)
                # side
                self.line(t0, b0)
                self.line(t1, b1)
                self.line(t2, b2)
                self.line(t3, b3)

    def bone(self, key, length: float, is_selected: bool = False) -> bool:
        '''
        return True if mouse clicked
        '''
        s = length * 0.1
        # head-tail
        #      0, -1(p1)
        # (p2)  |
        # -1, 0 |
        #     --+--->
        #       |    1, 0(p0)
        #       v
        #      0, +1(p3)
        self.color = glm.vec4(1, 0.0, 1, 1)
        h = glm.vec3(0, 0, 0)
        t = glm.vec3(0, length, 0)
        # self.line(h, t, bone.world_matrix)
        p0 = glm.vec3(s, s, 0)
        p1 = glm.vec3(0, s, -s)
        p2 = glm.vec3(-s, s, 0)
        p3 = glm.vec3(0, s, s)

        self.line(p0, p1)
        self.line(p1, p2)
        self.line(p2, p3)
        self.line(p3, p0)

        # self.line(p2, p0, bone.world_matrix)
        self.color = glm.vec4(1, 0, 0, 1)
        self.line(h, p0)
        self.line(p0, t)
        self.color = glm.vec4(0.1, 0, 0, 1)
        if is_selected:
            self.color = glm.vec4(0.1, 1, 0, 1)
        self.line(h, p2)
        self.line(p2, t)

        # self.line(p1, p3, bone.world_matrix)
        self.color = glm.vec4(0, 0, 1, 1)
        self.line(h, p3)
        self.line(p3, t)
        self.color = glm.vec4(0, 0, 0.1, 1)
        if is_selected:
            self.color = glm.vec4(0, 1, 0.1, 1)
        self.line(h, p1)
        self.line(p1, t)

        # triangles
        clicked = False
        self.color = glm.vec4(0.5, 0.5, 0.5, 0.2)
        if is_selected:
            self.color = glm.vec4(0.7, 0.7, 0, 0.7)
        elif self.hover_last == key:
            self.color = glm.vec4(0, 0.7, 0, 0.7)
            if self.click_left:
                clicked = True

        triangles = (
            (p0, h, p1),
            (p1, h, p2),
            (p2, h, p3),
            (p3, h, p0),
            (p0, t, p1),
            (p1, t, p2),
            (p2, t, p3),
            (p3, t, p0),
        )

        any_hit = False
        for t in triangles:
            hit = self.triangle(*t, intersect=(not any_hit))
            if hit:
                self.hover = key
                any_hit = True

        return clicked
