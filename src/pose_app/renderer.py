from OpenGL import GL
import pathlib
import formats.gltf_loader


class Renderer:
    def __init__(self) -> None:
        pass

    def load(self, path: pathlib.Path):
        print(path)
        gltf = formats.gltf_loader.Gltf.load_glb(path.read_bytes())
        print(gltf)

    def draw(self, *args):
        GL.glClearColor(1, 0, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
