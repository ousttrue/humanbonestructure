from typing import Optional
import logging
from OpenGL import GL
from glglue import ctypesmath
from glglue.gl3 import gizmo
from . import humanoid


LOGGER = logging.getLogger(__name__)


class HumanoidScene:
    def __init__(self, root: humanoid.Bone, on_selected):
        self.isInitialized = False
        self.root = root
        self.gizmo = gizmo.Gizmo()
        self.selected: Optional[humanoid.Bone] = None
        self.on_selected = on_selected

    def _initialize(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.isInitialized = True

    def _draw(self, bone: humanoid.Bone, parent: ctypesmath.Mat4):
        matrix = bone.local_euler_matrix() * bone.local_init_matrix * parent

        for i, child in enumerate(bone.children):
            if i == 0:
                self.gizmo.matrix = matrix
                # self.gizmo.matrix = bone.world_matrix
                if self.gizmo.bone(bone.bone, child.offset.get_length(), bone == self.selected):
                    if self.selected != bone:
                        self.selected = bone
                        self.on_selected(self.selected)

            self._draw(child, matrix)

    def draw(self, state: ctypesmath.FrameState):
        if not self.isInitialized:
            self._initialize()

        self.gizmo.begin(state)

        self.gizmo.axis(10)
        self._draw(self.root, ctypesmath.Mat4.new_identity())

        self.gizmo.end()


class SampleController:
    def __init__(self, root, scene_selected):
        self.clear_color = (0.6, 0.6, 0.4, 0.0)
        self.camera = ctypesmath.Camera()
        self.camera.view.y = -1.0
        self.camera.view.distance = 5.0
        self.camera.view.update_matrix()

        from . import humanoid_scene
        self.scene = humanoid_scene.HumanoidScene(
            root, scene_selected)
        self.isInitialized = False
        self.light = ctypesmath.Float4(1, 1, 1, 1)

    def onResize(self, w: int, h: int) -> bool:
        return self.camera.onResize(w, h)

    def onLeftDown(self, x: int, y: int) -> bool:
        ''' mouse input '''
        return self.camera.onLeftDown(x, y)

    def onLeftUp(self, x: int, y: int) -> bool:
        ''' mouse input '''
        return self.camera.onLeftUp(x, y)

    def onMiddleDown(self, x: int, y: int) -> bool:
        ''' mouse input '''
        return self.camera.onMiddleDown(x, y)

    def onMiddleUp(self, x: int, y: int) -> bool:
        ''' mouse input '''
        return self.camera.onMiddleUp(x, y)

    def onRightDown(self, x: int, y: int) -> bool:
        ''' mouse input '''
        return self.camera.onRightDown(x, y)

    def onRightUp(self, x: int, y: int) -> bool:
        ''' mouse input '''
        return self.camera.onRightUp(x, y)

    def onMotion(self, x: int, y: int) -> bool:
        ''' mouse input '''
        return self.camera.onMotion(x, y)

    def onWheel(self, d: int) -> bool:
        ''' mouse input '''
        return self.camera.onWheel(d)

    def onKeyDown(self, keycode: int) -> bool:
        return False

    def onUpdate(self, d: int) -> bool:
        '''
        milliseconds
        '''
        if not self.scene:
            return False
        return self.scene.update(d)

    def initialize(self):
        import glglue
        LOGGER.info(glglue.get_info())
        self.isInitialized = True

    def draw(self):
        if not self.isInitialized:
            self.initialize()
        GL.glClearColor(*self.clear_color)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT |
                   GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

        state = self.camera.get_state(self.light)
        GL.glViewport(int(state.viewport.x), int(state.viewport.y),
                      int(state.viewport.z), int(state.viewport.w))

        if self.scene:
            self.scene.draw(state)

        GL.glFlush()
