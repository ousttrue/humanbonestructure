from typing import Optional
from PySide6 import QtCore, QtWidgets, QtGui
from . import humanoid_scene
from . import humanoid


class HumanoidTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, root: humanoid.Bone):
        super().__init__()
        self.root = root

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        if parent.column() > 0:
            return 0
        parentItem = self.root
        if parent.isValid():
            parentItem = parent.internalPointer()
        return len(parentItem.children)

    def index(self, row, column, parent):
        parentItem = self.root
        if parent.isValid():
            parentItem = parent.internalPointer()
        try:
            child = parentItem.children[row]
            return self.createIndex(row, column, child)
        except IndexError:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            childItem = index.internalPointer()
            for i, bone in enumerate(self.root.traverse()):
                if childItem in bone.children:
                    return self.createIndex(i, 0, bone)
        return QtCore.QModelIndex()

    def headerData(self, section, orientation, role):
        match orientation, role:
            case QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole:
                return 'bone'

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                item = index.internalPointer()
                return item.bone.name


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, gui_scale: float = 1.0):
        super().__init__()
        self.setWindowTitle('humanoid view')
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        self.view_menu = menu.addMenu("&File")
        self.docks = {}
        self.root = humanoid.make_humanoid(1.0)

        # tree
        self.tree = QtWidgets.QTreeView()
        self.model = HumanoidTreeModel(self.root)
        self.tree.setModel(self.model)
        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)
        self._create_dock(QtCore.Qt.LeftDockWidgetArea, "bones", self.tree)

        # OpenGL
        import glglue.pyside6
        import glglue.gl3.samplecontroller
        self.controller = glglue.gl3.samplecontroller.SampleController()
        self.humanoid_scene = humanoid_scene.HumanoidScene(
            self.root)
        self.controller.scene = self.humanoid_scene
        self.glwidget = glglue.pyside6.Widget(
            self, self.controller, dpi_scale=gui_scale)
        self.setCentralWidget(self.glwidget)

    def _create_dock(self, area, name, widget):
        dock = QtWidgets.QDockWidget(name, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        self.view_menu.addAction(dock.toggleViewAction())
        self.docks[area] = dock