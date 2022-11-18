import sys
import pathlib
import gi
from .renderer import Renderer
import traceback

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
from gi.repository import Gtk, Gio  # type: ignore


class Window(Gtk.ApplicationWindow):
    def __init__(self, app) -> None:
        super().__init__(application=app, title="HumanPose")  # type: ignore

        self.renderer = Renderer()

        self.gl = Gtk.GLArea()
        self.gl.connect("render", self.renderer.draw)

        self.set_child(self.gl)


def on_activate(app: Gtk.Application) -> None:
    try:
        window = Window(app)
        if len(sys.argv) > 1:
            window.renderer.load(pathlib.Path(sys.argv[1]))
        window.present()
    except Exception:
        traceback.print_exc()
        sys.exit()


def main():
    app = Gtk.Application.new(
        application_id="com.ousttrue.humanpose",
        flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
    )
    app.connect("activate", on_activate)
    app.run()  # type: ignore
