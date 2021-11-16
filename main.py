import enum
import sys
import pathlib
from PySide6 import QtCore, QtWidgets, QtGui, QtCharts
import bvh_parser


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


class BvhView(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('bvh view')

        # OpenGL
        import glglue.gl3
        self.controller = glglue.gl3.SampleController()
        import glglue.pyside6
        self.glwidget = glglue.pyside6.Widget(self, self.controller)
        # self.setCentralWidget(self.glwidget)
        self.gl_dock = QtWidgets.QDockWidget('OpenGL', self)
        self.gl_dock.setWidget(self.glwidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.gl_dock)

        # BvhNodeTree
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Name", "Offset", "Channels"])
        self.tree_dock = QtWidgets.QDockWidget('bvh hierarchy', self)
        self.tree_dock.setWidget(self.tree)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.tree_dock)

        # BvhFrameList
        self.table = QtWidgets.QTableView()
        self.table_dock = QtWidgets.QDockWidget('bvh frames', self)
        self.table_dock.setWidget(self.table)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.table_dock)

        # FrameChart
        self.chart = QtCharts.QChart()
        self.chart_view = QtCharts.QChartView(self.chart)        
        self.setCentralWidget(self.chart_view)
        self.serieses = []

        # menu
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        open_action = QtGui.QAction("&Open", self)
        open_action.triggered.connect(self.open_dialog)  # type: ignore
        file_menu.addAction(open_action)

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
        self.model = BvhFrameTableModel(bvh)
        self.table.setModel(self.model)

        # chart
        for s in self.serieses:
            self.chart.removeSeries(s)
        self.serieses.clear()
        channel_count = bvh.root.get_channel_count()
        def add_seriese(name: str, index: int):
            series = QtCharts.QLineSeries()
            series.setName(name)
            for i in range(bvh.frames):
                value = bvh.data[i * channel_count + index]
                series.append(i, value)
            self.serieses.append(series)
            self.chart.addSeries(series)
        i = 0
        for node in bvh.root.traverse():
            match node.channels:
                case bvh_parser.Channels.PosXYZ_RotZXY:
                    add_seriese(f'{node.name}.pos.x', i)
                    i+=1
                    add_seriese(f'{node.name}.pos.y', i)
                    i+=1
                    add_seriese(f'{node.name}.pos.z', i)
                    i+=1
                    add_seriese(f'{node.name}.rot.z', i)
                    i+=1
                    add_seriese(f'{node.name}.rot.x', i)
                    i+=1
                    add_seriese(f'{node.name}.rot.y', i)
                    i+=1
                case bvh_parser.Channels.RotZXY:
                    add_seriese(f'{node.name}.rot.z', i)
                    i+=1
                    add_seriese(f'{node.name}.rot.x', i)
                    i+=1
                    add_seriese(f'{node.name}.rot.y', i)
                    i+=1
                

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

    widget = BvhView()
    widget.resize(1024, 768)
    widget.show()

    sys.exit(app.exec())
