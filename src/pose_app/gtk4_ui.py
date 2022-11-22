import sys
import pathlib
import gi
import traceback

gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
from gi.repository import GLib, Gtk, Gio  # type: ignore


class UdpReceiver(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # port listen
        port_listen = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.port = Gtk.SpinButton.new_with_range(0, 65535, 1)
        self.port.set_value(1505)
        port_listen.append(self.port)
        self.listen = Gtk.Button.new()
        self.listen.set_label("listen")
        self.listen.connect("clicked", self.on_listen)
        port_listen.append(self.listen)
        self.append(port_listen)

        # udp
        self.received = Gtk.Text.new()
        self.received.set_vexpand(True)
        self.append(self.received)

    def on_listen(self, *args):
        if self.listen.get_label() == "listen":
            port = int(self.port.get_value())

            addr = Gio.InetSocketAddress.new(
                Gio.InetAddress.new_any(Gio.SocketFamily.IPV4), port
            )
            assert addr
            self.received.set_text(f"listen: localhost:{port}")

            self.socket = Gio.Socket.new(
                Gio.SocketFamily.IPV4, Gio.SocketType.DATAGRAM, Gio.SocketProtocol.UDP
            )
            assert self.socket

            if not self.socket.bind(addr, False):
                raise Exception("fail to bind")

            channel = GLib.IOChannel.win32_new_socket(self.socket.get_fd())
            self.watch = GLib.io_add_watch(
                channel, GLib.IOCondition.IN, self.on_read_socket, None
            )

            self.is_listening = True
            self.listen.set_label("stop")
        else:
            self.socket.close()
            self.socket = None
            # TODO: on_closed
            self.listen.set_label("listen")

    def on_read_socket(
        self, channel: GLib.IOChannel, condition: GLib.IOCondition, data
    ) -> bool:
        if condition & GLib.IOCondition.HUP:
            # this channel is done
            return False

        data = channel.read(1024)
        self.received.set_text(data.decode("utf-8"))
        return True


class Window(Gtk.ApplicationWindow):
    def __init__(self, app) -> None:
        super().__init__(application=app, title="HumanPose")  # type: ignore

        paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.set_child(paned)

        # left
        left = UdpReceiver()
        paned.set_start_child(left)

        # right
        from .renderer import Renderer
        import glglue.gtk4

        self.renderer = Renderer()
        self.gl = glglue.gtk4.GLArea(self.renderer.draw)
        self.gl.set_size_request(200, 200)
        paned.set_end_child(self.gl)


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
