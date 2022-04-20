import logging
from glglue import ctypesmath
from OpenGL import GL


LOGGER = logging.getLogger(__name__)


class Scene:
    def __init__(self) -> None:
        self.env = []
        # from ..scene import cube
        self.drawables = []
        from glglue.gl3.renderer import Renderer
        self.renderer = Renderer()
        from glglue.gl3 import gizmo
        self.gizmo = gizmo.Gizmo()

    def __del__(self):
        del self.renderer

    def update(self, d: int) -> bool:
        updated = False
        for drawable in self.drawables:
            if drawable.update(d):
                updated = True
        return updated

    def draw(self, state):
        self.gizmo.begin(state)
        self.gizmo.axis(10)

        for e in self.env:
            self.renderer.draw(e, state)
        for _, drawable in enumerate(self.drawables):
            self.renderer.draw(drawable, state)
            # aabb
            aabb = ctypesmath.AABB.new_empty()
            self.gizmo.aabb(drawable.expand_aabb(aabb))

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
