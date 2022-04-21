from typing import Optional
import logging
from OpenGL import GL
import glm
from pydear.scene.camera import Camera
from pydear.scene.bone_gizmo import BoneGizmo
from . import humanoid


LOGGER = logging.getLogger(__name__)


class BoneScene:
    def __init__(self, root, scene_selected):
        self.clear_color = (0.6, 0.6, 0.4, 0.0)
        self.camera = Camera(y=-1.0, distance=5.0)

        self.root = root
        self.gizmo = BoneGizmo()
        self.selected: Optional[humanoid.Bone] = None
        self.on_selected = scene_selected

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

    def _draw(self, bone: humanoid.Bone, parent: glm.mat4):
        matrix = parent * bone.local_init_matrix * bone.local_euler_matrix()

        for i, child in enumerate(bone.children):
            if i == 0:
                self.gizmo.matrix = glm.mat4(*matrix)
                # self.gizmo.matrix = bone.world_matrix
                if self.gizmo.bone(bone.bone, glm.length(child.offset), bone == self.selected):
                    if self.selected != bone:
                        self.selected = bone
                        self.on_selected(self.selected)

            self._draw(child, matrix)

    def draw(self):
        GL.glClearColor(*self.clear_color)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT |
                   GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

        GL.glViewport(0, 0, self.camera.projection.width,
                      self.camera.projection.height)

        GL.glEnable(GL.GL_DEPTH_TEST)

        self.gizmo.begin(
            self.x,
            self.y,
            self.left,
            self.right,
            self.middle,
            self.camera.view.matrix,
            self.camera.projection.matrix,
            self.camera.get_mouse_ray(self.x, self.y))

        self.gizmo.axis(10)
        self._draw(self.root, glm.mat4())

        self.gizmo.end()
