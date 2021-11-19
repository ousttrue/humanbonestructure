import sys
import pathlib
from PySide6 import QtCore, QtWidgets, QtGui
from . import bvh_parser
from . import bvh_scene
from . import humanoid_widget
from . import gl_multiview


class Playback(QtWidgets.QWidget):
    '''
    [play][stop][time][progress bar]
    '''
    frame_changed = QtCore.Signal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.start = QtWidgets.QPushButton("Start", self)
        self.progressBar = QtWidgets.QProgressBar(self)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.start)
        layout.addWidget(self.progressBar)
        self.setLayout(layout)

    def set_bvh(self, bvh: bvh_parser.Bvh):
        self.progressBar.setRange(0, bvh.frames)
        # Construct a 1-second timeline with a frame range of 0 - 100
        timeLine = QtCore.QTimeLine(int(bvh.get_seconds() * 1000), self)
        timeLine.setFrameRange(0, bvh.frames)
        timeLine.frameChanged.connect(  # type: ignore
            self.progressBar.setValue)
        timeLine.frameChanged.connect(self.frame_changed)  # type: ignore
        # Clicking the push button will start the progress bar animation
        self.start.clicked.connect(timeLine.start)  # type: ignore


class BvhView(QtWidgets.QMainWindow):
    def __init__(self, gui_scale: float = 1.0):
        super().__init__()
        self.setWindowTitle('bvh view')
        self.docks = {}

        #
        # Left
        #
        self._create_dock(
            QtCore.Qt.LeftDockWidgetArea, 'bvh', self._create_left())

        #
        # Right
        #
        self.humanoid = humanoid_widget.HumanoidWiget(self)
        self._create_dock(
            QtCore.Qt.RightDockWidgetArea, 'humanoid', self.humanoid)

        #
        # Bottom
        #
        self.bottom_dock = self._create_dock(
            QtCore.Qt.BottomDockWidgetArea, 'timeline', self._create_bottom()
        )

        #
        # Central
        #
        self.gl_controller = gl_multiview.MultiViewController(gui_scale)
        import glglue.pyside6
        self.glwidget = glglue.pyside6.Widget(self, self.gl_controller)
        self.setCentralWidget(self.glwidget)

        self.bvh_scene = bvh_scene.BvhScene()
        view = self.gl_controller.pushScene(self.bvh_scene)
        view.camera.projection.z_far *= 100
        view.camera.view.distance *= 100
        self.gl_controller.pushScene(self.humanoid.humanoid_scene)

        # menu
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        open_action = QtGui.QAction("&Open", self)
        open_action.triggered.connect(self.open_dialog)  # type: ignore
        file_menu.addAction(open_action)

    def _create_dock(self, area, name, widget):
        dock = QtWidgets.QDockWidget(name, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        self.docks[area] = dock

    def _create_left(self) -> QtWidgets.QWidget:
        # BvhNodeTree
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Name", "Offset", "Channels"])
        return self.tree

    def _create_bottom(self) -> QtWidgets.QWidget:
        # BvhFrameList
        self.playback = Playback(self)
        # self.table = QtWidgets.QTableView()
        w = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(w)
        layout.addWidget(self.playback)
        # layout.addWidget(self.table)
        w.setLayout(layout)
        return w

    def open(self, path: pathlib.Path):
        if not path.exists():
            return

        bvh = bvh_parser.parse(path.read_text(encoding='utf-8'))
        self.setWindowTitle(f'{path.name} {bvh.get_seconds()}seconds')

        # hierarchy
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

        self.bvh_scene.load(bvh)
        self.playback.set_bvh(bvh)
        self.glwidget.repaint()
        self.playback.frame_changed.connect(self.set_frame)  # type: ignore

    def set_frame(self, frame: int):
        self.bvh_scene.set_frame(frame)
        self.glwidget.repaint()

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


def run():
    app = QtWidgets.QApplication(sys.argv)

    widget = BvhView(1.5)
    widget.resize(1024, 768)
    widget.show()

    sys.exit(app.exec())
