from PySide6 import QtWidgets
import pathlib
from .main_widget import MainWidget


def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # import glglue.utils
    # dpi_scale = glglue.utils.get_desktop_scaling_factor()
    dpi_scale = 1.5

    widget = MainWidget(dpi_scale)
    widget.resize(1024, 768)
    widget.show()

    if len(sys.argv) > 1:
        widget.open(pathlib.Path(sys.argv[1]))

    sys.exit(app.exec())
