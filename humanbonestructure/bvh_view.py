import sys
import pathlib
from PySide6 import QtCore, QtWidgets, QtGui
from . import bvh_parser
from . import bvh_controller
from . import humanoid_widget

class BvhFrameTableModel(QtCore.QAbstractTableModel):
    def __init__(self, bvh: bvh_parser.Bvh):
        super().__init__()
        self.bvh = bvh
        self.channels = []
        for node in self.bvh.root.traverse():
            match node.channels:
                case bvh_parser.Channels.PosXYZ_RotZXY:
                    self.channels.append(f'{node.name}.pos.x')
                    self.channels.append(f'{node.name}.pos.y')
                    self.channels.append(f'{node.name}.pos.z')
                    self.channels.append(f'{node.name}.rot.z')
                    self.channels.append(f'{node.name}.rot.x')
                    self.channels.append(f'{node.name}.rot.y')
                case bvh_parser.Channels.RotZXY:
                    self.channels.append(f'{node.name}.rot.z')
                    self.channels.append(f'{node.name}.rot.x')
                    self.channels.append(f'{node.name}.rot.y')

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.channels)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.bvh.frames

    def headerData(self, section, orientation, role):
        match orientation, role:
            case QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole:
                return f'{section}'
            case QtCore.Qt.Vertical, QtCore.Qt.DisplayRole:
                return self.channels[section]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == QtCore.Qt.DisplayRole:
            return self.bvh.data[row * len(self.channels) + column]
        elif role == QtCore.Qt.BackgroundRole:
            return QtGui.QColor(QtCore.Qt.white)
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignRight

        return None


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
    def __init__(self):
        super().__init__()
        self.setWindowTitle('bvh view')

        # humanoid
        self.humanoid = humanoid_widget.HumanoidWiget(self)
        self.setCentralWidget(self.humanoid)

        #
        # Left
        #
        left = self._create_left()
        self.left_dock = self._create_dock(
            QtCore.Qt.LeftDockWidgetArea, 'bvh', left)

        #
        # Bottom
        #
        bottom = self._create_bottom()
        self.bottom_dock = self._create_dock(
            QtCore.Qt.BottomDockWidgetArea, 'timeline', bottom
        )

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
        return dock

    def _create_left(self) -> QtWidgets.QWidget:
        splitter = QtWidgets.QSplitter(self)

        # OpenGL
        self.bvh_controller = bvh_controller.BvhController()
        import glglue.pyside6
        self.glwidget = glglue.pyside6.Widget(self, self.bvh_controller)
        splitter.insertWidget(0, self.glwidget)

        # BvhNodeTree
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Name", "Offset", "Channels"])
        splitter.insertWidget(0, self.tree)

        return splitter

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

        # frames
        # self.model = BvhFrameTableModel(bvh)
        # self.table.setModel(self.model)

        # chart
        # for s in self.serieses:
        #     self.chart.removeSeries(s)
        # self.serieses.clear()
        # channel_count = bvh.root.get_channel_count()
        # def add_seriese(name: str, index: int):
        #     series = QtCharts.QLineSeries()
        #     series.setName(name)
        #     for i in range(bvh.frames):
        #         value = bvh.data[i * channel_count + index]
        #         series.append(i, value)
        #     self.serieses.append(series)
        #     self.chart.addSeries(series)
        # i = 0
        # for node in bvh.root.traverse():
        #     match node.channels:
        #         case bvh_parser.Channels.PosXYZ_RotZXY:
        #             add_seriese(f'{node.name}.pos.x', i)
        #             i+=1
        #             add_seriese(f'{node.name}.pos.y', i)
        #             i+=1
        #             add_seriese(f'{node.name}.pos.z', i)
        #             i+=1
        #             add_seriese(f'{node.name}.rot.z', i)
        #             i+=1
        #             add_seriese(f'{node.name}.rot.x', i)
        #             i+=1
        #             add_seriese(f'{node.name}.rot.y', i)
        #             i+=1
        #         case bvh_parser.Channels.RotZXY:
        #             add_seriese(f'{node.name}.rot.z', i)
        #             i+=1
        #             add_seriese(f'{node.name}.rot.x', i)
        #             i+=1
        #             add_seriese(f'{node.name}.rot.y', i)
        #             i+=1

        self.bvh_controller.load(bvh)
        self.playback.set_bvh(bvh)
        self.glwidget.repaint()
        self.playback.frame_changed.connect(self.set_frame)  # type: ignore

    def set_frame(self, frame: int):
        self.bvh_controller.set_frame(frame)
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
    app = QtWidgets.QApplication([])

    widget = BvhView()
    widget.resize(1024, 768)
    widget.show()

    sys.exit(app.exec())
