from OpenGL import GL
from pydear.scene.camera import Camera
from pydear.scene.gizmo import Gizmo

from ..formats import bvh_parser
from . import bvh_skeleton


class BvhScene:
    def __init__(self):
        self.clear_color = (0.6, 0.6, 0.4, 0.0)
        self.camera = Camera(distance=200.0)
        self.skeleton = None
        self.gizmo = Gizmo()

        self.x = 0
        self.y = 0
        self.left = False
        self.right = False
        self.middle = False

    def onResize(self, w: int, h: int) -> bool:
        return self.camera.projection.resize(w, h)

    def onLeftDown(self, x: int, y: int) -> bool:
        ''' mouse input '''
        self.left = True
        self.x = x
        self.y = y
        return False

    def onLeftUp(self, x: int, y: int) -> bool:
        ''' mouse input '''
        self.left = False
        self.x = x
        self.y = y
        return False

    def onMiddleDown(self, x: int, y: int) -> bool:
        ''' mouse input '''
        self.middle = True
        self.x = x
        self.y = y
        return False

    def onMiddleUp(self, x: int, y: int) -> bool:
        ''' mouse input '''
        self.middle = False
        self.x = x
        self.y = y
        return False

    def onRightDown(self, x: int, y: int) -> bool:
        ''' mouse input '''
        self.right = True
        self.x = x
        self.y = y
        return False

    def onRightUp(self, x: int, y: int) -> bool:
        ''' mouse input '''
        self.right = False
        self.x = x
        self.y = y
        return False

    def onMotion(self, x: int, y: int) -> bool:
        ''' mouse input '''
        dx = x - self.x
        dy = y - self.y
        self.camera.mouse_drag(x, y, dx, dy, self.left,
                               self.right, self.middle)
        self.x = x
        self.y = y
        return True

    def onWheel(self, d: int) -> bool:
        ''' mouse input '''
        self.camera.wheel(-d)
        return True

    def onKeyDown(self, keycode: int) -> bool:
        return False

    def onUpdate(self, d: int) -> bool:
        '''
        milliseconds
        '''
        return False

    def load(self, bvh: bvh_parser.Bvh):
        self.skeleton = bvh_skeleton.BvhSkeleton(bvh)

    def set_frame(self, frame: int):
        if self.skeleton:
            self.skeleton.set_frame(frame)

    def draw(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(*self.clear_color)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT |
                   GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

        GL.glViewport(0, 0, self.camera.projection.width,
                      self.camera.projection.height)

        # GL.glEnable(GL.GL_DEPTH_TEST)

        self.gizmo.begin(
            self.x,
            self.y,
            self.left,
            self.camera.view.matrix,
            self.camera.projection.matrix,
            self.camera.get_mouse_ray(self.x, self.y))

        if self.skeleton:
            self.skeleton.draw(self.camera)

        self.gizmo.axis(10)

        self.gizmo.end()

    def expand_aabb(self, aabb):
        return aabb
