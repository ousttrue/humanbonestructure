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

        self.gl = Gtk.GLArea()
        self.renderer = Renderer(self.gl.queue_render)
        self.gl.connect("render", self.on_render)
        # motion
        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("motion", self.renderer.on_motion)
        self.gl.add_controller(motion_controller)
        # left
        left_click_controller = Gtk.GestureClick()
        left_click_controller.set_button(1)
        left_click_controller.connect("pressed", self.renderer.on_left_down, self.gl)
        left_click_controller.connect("released", self.renderer.on_left_up, self.gl)
        self.gl.add_controller(left_click_controller)
        # middle
        middle_click_controller = Gtk.GestureClick()
        middle_click_controller.set_button(2)
        middle_click_controller.connect(
            "pressed", self.renderer.on_middle_down, self.gl
        )
        middle_click_controller.connect("released", self.renderer.on_middle_up, self.gl)
        self.gl.add_controller(middle_click_controller)
        # right
        right_click_controller = Gtk.GestureClick()
        right_click_controller.set_button(3)
        right_click_controller.connect("pressed", self.renderer.on_right_down, self.gl)
        right_click_controller.connect("released", self.renderer.on_right_up, self.gl)
        self.gl.add_controller(right_click_controller)
        # wheel
        wheel_controller = Gtk.EventControllerScroll()
        wheel_controller.set_flags(Gtk.EventControllerScrollFlags.VERTICAL)
        wheel_controller.connect("scroll", self.renderer.on_wheel)
        self.gl.add_controller(wheel_controller)
        self.set_child(self.gl)

    def on_render(self, area, context):
        self.renderer.draw(
            self.get_size(Gtk.Orientation.HORIZONTAL),
            self.get_size(Gtk.Orientation.VERTICAL),
        )


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
