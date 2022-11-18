from OpenGL import GL
import pathlib


class Renderer:
    def __init__(self) -> None:
        pass

    def load(self, path: pathlib.Path):
        print(path)

    def draw(self, *args):
        GL.glClearColor(1, 0, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
