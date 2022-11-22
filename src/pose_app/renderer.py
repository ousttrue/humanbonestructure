from OpenGL import GL
import logging
import pathlib
import formats.gltf_loader
from builder import gltf_builder
from glglue.camera import MouseCamera
import glglue.frame_input

logger = logging.getLogger(__name__)


class Renderer:
    def __init__(self) -> None:
        self.model = None
        self.camera = MouseCamera(distance=5, y=-1)

    def load(self, path: pathlib.Path):
        logger.info(path)
        self.model = formats.gltf_loader.Gltf.load_glb(path.read_bytes())
        logger.info(self.model)
        self.hierarchy = gltf_builder.build(self.model)
        self.skeleton = self.hierarchy.to_skeleton()

    def draw(self, frame: glglue.frame_input.FrameInput):
        # update camera
        self.camera.process(frame)

        GL.glViewport(0, 0, frame.width, frame.height)
        GL.glClearColor(1, 0, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

        self.hierarchy.render(self.camera.camera)
