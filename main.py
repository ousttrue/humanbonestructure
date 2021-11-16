import sys
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

    def create_central(self) -> QtWidgets.QWidget:
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Name", "Offset", "Channels"])
        return self.tree

    def open(self, path: pathlib.Path):
        if not path.exists():
            return
        print(path)
        bvh = bvh_parser.parse(path.read_text(encoding='utf-8'))

        def build_tree(items, node: bvh_parser.Node):
            item = QtWidgets.QTreeWidgetItem(
                [node.name, str(node.offset),
                 str(node.channels)])
            for child in node.children:
                if (child.name):
                    child_item = build_tree(items, child)
                    item.addChild(child_item)

            items.append(item)
            return item

        items = []
        build_tree(items, bvh.root)
        self.tree.clear()
        self.tree.insertTopLevelItems(0, items)
        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)
        self.tree.resizeColumnToContents(2)

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


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
