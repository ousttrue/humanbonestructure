from PySide6 import QtWidgets
from .main_widget import MainWidget


def run():
    from logging import basicConfig, DEBUG
    basicConfig(format='%(levelname)s:%(name)s:%(message)s', level=DEBUG)

    import sys
    app = QtWidgets.QApplication(sys.argv)

    # import glglue.utils
    # dpi_scale = glglue.utils.get_desktop_scaling_factor()
    dpi_scale = 1.5

    widget = MainWidget(dpi_scale)
    widget.resize(1024, 768)
    widget.show()

    sys.exit(app.exec())
