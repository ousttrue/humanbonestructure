from dataclasses import dataclass
from typing import List, NamedTuple, Optional, Tuple
from OpenGL import GL
import glglue.basecontroller
import glglue.ctypesmath
from . import gl_scene


class Rect(NamedTuple):
    x: int
    y: int
    width: int
    height: int

    def contains(self, x, y) -> Optional[Tuple[int, int]]:
        if x < self.x:
            return
        x -= self.x
        if x > self.width:
            return
        if y < self.y:
            return
        y -= self.y
        if y > self.height:
            return
        return (x, y)


class ScreenView:
    def __init__(self, scene):
        self.scene = scene
        self.rect = Rect(0, 0, 1, 1)
        self.camera = glglue.ctypesmath.Camera()
        self.isInitialized = False
        self.clear_color = [0.6, 0.4, 0.2, 0]

    def setViewport(self, x, y, w, h):
        self.rect = Rect(int(x), int(y), int(w), int(h))
        self.camera.onResize(w, h)

    def initialize(self):
        self.isInitialized = True

    def draw(self):
        if not self.isInitialized:
            self.initialize()

        # clear
        GL.glEnable(GL.GL_SCISSOR_TEST)
        GL.glScissor(*self.rect)
        GL.glClearColor(*self.clear_color)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT |
                   GL.GL_DEPTH_BUFFER_BIT)  # type: ignore
        GL.glDisable(GL.GL_SCISSOR_TEST)

        # draw
        GL.glViewport(*self.rect)
        self.scene.draw(self.camera.projection.matrix, self.camera.view.matrix)


class MultiViewController(glglue.basecontroller.BaseController):
    '''
    * focusに応じて、複数のビューにマウスイベントを分配する
    '''

    def __init__(self, gui_scale: float):
        self.rect = Rect(0, 0, 1, 1)
        self.views: List[ScreenView] = []
        self.focus: Optional[ScreenView] = None
        self.last_focus: Optional[ScreenView] = None
        self.leftDown = False
        self.middleDown = False
        self.rightDown = False
        self.gui_scale = gui_scale

    def onResize(self, w: int, h: int) -> bool:
        w, h = self._guiScale(w, h)
        self.rect = Rect(0, 0, w, h)

        # split vertical
        if not self.views:
            return False
        ww = w // len(self.views)
        if ww == 0:
            ww = 1
        x = 0
        repaint = False
        for v in self.views:
            if v.setViewport(x, 0, ww, h):
                repaint = True
            x += ww

        return repaint

    def pushScene(self, scene: gl_scene.Scene) -> ScreenView:
        view = ScreenView(scene)
        self.views.append(view)
        self.onResize(self.rect.width, self.rect.height)
        return view

    def _getFocus(self, x, y, set_focus=False) -> Optional[Tuple[ScreenView, int, int]]:
        if self.focus:
            return (self.focus, x-self.focus.rect.x, y-self.focus.rect.y)
        for i, view in enumerate(self.views):
            xy = view.rect.contains(x, y)
            if xy:
                if set_focus:
                    self.focus = view
                return (view, *xy)

    def _mouseUp(self):
        if not self.focus:
            return
        if self.leftDown or self.middleDown or self.rightDown:
            return

        self.last_focus = self.focus
        self.focus = None

    def _guiScale(self, *values):
        return [value * self.gui_scale for value in values]

    def onLeftDown(self, x: int, y: int) -> bool:
        """mouse input"""
        x, y = self._guiScale(x, y)
        self.leftDown = True
        match self._getFocus(x, y, True):
            case view, x, y:
                return view.camera.onLeftDown(x, y)
            case _:
                return False

    def onLeftUp(self, x: int, y: int) -> bool:
        """mouse input"""
        x, y = self._guiScale(x, y)
        self.leftDown = False
        match self._getFocus(x, y):
            case view, x, y:
                self._mouseUp()
                return view.camera.onLeftUp(x, y)
            case _:
                return False

    def onMiddleDown(self, x: int, y: int) -> bool:
        """mouse input"""
        x, y = self._guiScale(x, y)
        self.middleDown = True
        match self._getFocus(x, y, True):
            case view, x, y:
                return view.camera.onMiddleDown(x, y)
            case _:
                return False

    def onMiddleUp(self, x: int, y: int) -> bool:
        """mouse input"""
        x, y = self._guiScale(x, y)
        self.middleDown = False
        match self._getFocus(x, y):
            case view, x, y:
                self._mouseUp()
                return view.camera.onMiddleUp(x, y)
            case _:
                return False

    def onRightDown(self, x: int, y: int) -> bool:
        """mouse input"""
        x, y = self._guiScale(x, y)
        self.rightDown = True
        match self._getFocus(x, y, True):
            case view, x, y:
                return view.camera.onRightDown(x, y)
            case _:
                return False

    def onRightUp(self, x: int, y: int) -> bool:
        """mouse input"""
        x, y = self._guiScale(x, y)
        self.rightDown = False
        match self._getFocus(x, y):
            case view, x, y:
                self._mouseUp()
                return view.camera.onRightUp(x, y)
            case _:
                return False

    def onMotion(self, x: int, y: int) -> bool:
        """mouse input"""
        x, y = self._guiScale(x, y)
        match self._getFocus(x, y):
            case view, x, y:
                return view.camera.onMotion(x, y)
            case _:
                return False

    def onWheel(self, d: int) -> bool:
        """mouse input"""
        if not self.views:
            return False
        if self.focus:
            return self.focus.camera.onWheel(d)
        if self.last_focus:
            return self.last_focus.camera.onWheel(d)
        return self.views[0].camera.onWheel(d)

    def onKeyDown(self, keycode: int) -> bool:
        return False

    def onUpdate(self, d: int) -> bool:
        """
        milliseconds
        """
        return False

    def draw(self):
        for view in self.views:
            view.draw()
        GL.glFlush()
