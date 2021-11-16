import sys
import random
import pathlib
from PySide6 import QtCore, QtWidgets, QtGui
import bvh_parser


def print_bvh(node: bvh_parser.Node, indent=''):
    print(f'{indent}{node}')
    indent += '  '
    for child in node.children:
        print_bvh(child, indent)


class MyWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(self.create_central())

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        open_action = QtGui.QAction("&Open", self)
        open_action.triggered.connect(self.open_dialog)  # type: ignore
        file_menu.addAction(open_action)

        toolbar = QtWidgets.QToolBar("My main toolbar")
        self.addToolBar(toolbar)
        button_action = QtGui.QAction("Click me!", self)
        button_action.setStatusTip("rundom text")
        button_action.triggered.connect(self.magic)  # type: ignore
        toolbar.addAction(button_action)

    def create_central(self) -> QtWidgets.QWidget:
        layout = QtWidgets.QVBoxLayout()

        self.text = QtWidgets.QLabel(
            "Hello World", alignment=QtCore.Qt.AlignCenter)  # type: ignore
        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]
        layout.addWidget(self.text)

        self.button = QtWidgets.QPushButton("Click me!")
        self.button.clicked.connect(self.magic)  # type: ignore
        layout.addWidget(self.button)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def open(self, path: pathlib.Path):
        if not path.exists():
            return
        print(path)
        bvh = bvh_parser.parse(path.read_text(encoding='utf-8'))
        print_bvh(bvh.root)

    @QtCore.Slot()  # type: ignore
    def open_dialog(self):
        dialog = QtWidgets.QFileDialog(self, caption="open bvh")
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setNameFilters(["bvh files (*.bvh)", "Any files (*)"])
        if not dialog.exec():
            return
        files = dialog.selectedFiles()
        if not files:
            return
        self.open(pathlib.Path(files[0]))

    @QtCore.Slot()  # type: ignore
    def magic(self):
        self.text.setText(random.choice(self.hello))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
