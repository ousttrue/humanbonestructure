from OpenGL import GL
import logging
import pathlib
import formats.gltf_loader
from builder import gltf_builder
from scene.scene import Scene
from scene.camera import Camera

logger = logging.getLogger(__name__)


class Renderer:
    def __init__(self) -> None:
        self.model = None
        self.camera = Camera(distance=5, y=1)

    def load(self, path: pathlib.Path):
        logger.info(path)
        self.model = formats.gltf_loader.Gltf.load_glb(path.read_bytes())
        logger.info(self.model)
        self.hierarchy = gltf_builder.build(self.model)
        self.skeleton = self.hierarchy.to_skeleton()

    def draw(self, *args):
        GL.glClearColor(1, 0, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        self.hierarchy.render(self.camera)
