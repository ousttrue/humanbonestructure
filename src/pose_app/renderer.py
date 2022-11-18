from OpenGL import GL
import logging
import pathlib
import formats.gltf_loader
from builder import gltf_builder
from scene.camera import Camera

logger = logging.getLogger(__name__)


class Renderer:
    def __init__(self, on_update) -> None:
        self.model = None
        self.camera = Camera(distance=5, y=0)
        self.left_down = False
        self.right_down = False
        self.middle_down = False
        self.x = 0
        self.y = 0
        self.on_update = on_update

    def load(self, path: pathlib.Path):
        logger.info(path)
        self.model = formats.gltf_loader.Gltf.load_glb(path.read_bytes())
        logger.info(self.model)
        self.hierarchy = gltf_builder.build(self.model)
        self.skeleton = self.hierarchy.to_skeleton()

    def on_motion(self, c, x, y):
        # print(x, y)
        dx = x - self.x
        dy = y - self.y
        if self.left_down:
            pass
        if self.right_down:
            self.camera.yaw_pitch(dx, dy)
        if self.middle_down:
            self.camera.shift(dx, dy)
        self.x = x
        self.y = y

    def on_left_down(self, *args):
        self.left_down = True

    def on_left_up(self, *args):
        self.left_down = False

    def on_middle_down(self, *args):
        self.middle_down = True

    def on_middle_up(self, *args):
        self.middle_down = False

    def on_right_down(self, *args):
        self.right_down = True

    def on_right_up(self, *args):
        self.right_down = False

    def on_wheel(self, c, x, y):
        self.camera.dolly(y)
        self.on_update()

    def draw(self, w, h):
        # update camera
        self.camera.projection.resize(w, h)

        GL.glViewport(0, 0, w, h)
        GL.glClearColor(1, 0, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT) # type: ignore

        self.hierarchy.render(self.camera)
