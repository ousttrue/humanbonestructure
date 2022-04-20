from typing import Dict, Any
import logging
from PySide6 import QtCore, QtWidgets, QtGui
from . import humanoid
from . import humanoid_tree
from .props import BoneProp


logger = logging.getLogger(__name__)


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, gui_scale: float = 1.0):
        super().__init__()
        self.setWindowTitle('humanoid view')
        menu = self.menuBar()
        view_menu = menu.addMenu("&View")
        self.view_menu = menu.addMenu("&File")
        self.docks: Dict[Any, QtWidgets.QDockWidget] = {}
        self.root = humanoid.make_humanoid(1.0)

        self._create_tree()
        gl = self._create_gl(gui_scale)
        self.prop = BoneProp(self)

        self.setCentralWidget(self.tree)
        self._create_dock(
            QtCore.Qt.LeftDockWidgetArea, "view", self.glwidget)
        self._create_dock(QtCore.Qt.RightDockWidgetArea, "prop", self.prop)

        def on_value_changed():
            gl.repaint()
        self.prop.value_changed.connect(on_value_changed)  # type: ignore

        for _, v in self.docks.items():
            view_menu.addAction(v.toggleViewAction())

        # logger
        import glglue.pyside6
        self.logger = glglue.pyside6.QPlainTextEditLogger(self)
        logging.getLogger('').addHandler(self.logger.log_handler)
        dock_bottom = self._create_dock(
            QtGui.Qt.BottomDockWidgetArea, "logger", self.logger)

        # render loop
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.glwidget.update)  # type: ignore
        self.timer.start(33)

    def _create_tree(self):
        self.tree = QtWidgets.QTreeView()

        # add_root
        root = humanoid.Bone(humanoid.HumanBones.EndSite,
                             humanoid.Float3(0, 0, 0), [self.root])
        self.model = humanoid_tree.HumanoidTreeModel(root)
        self.tree.setModel(self.model)
        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)

        self.tree.selectionModel().selectionChanged.connect(  # type: ignore
            self._on_selected)

        return self.tree

    def _scene_selected(self, bone):
        self.tree.selectionModel().clearSelection()
        if bone:
            #self.tree.selectionModel().select(self.model.createIndex(0, 0, selected))
            logger.info(f'select {bone.bone}')
            index = []

            def find(current: humanoid.Bone):
                for i, child in enumerate(current.children):
                    if child == bone:
                        index.append(self.model.createIndex(i, 0, child))
                        return True
                    if find(child):
                        return True
            find(self.root)
            if index:
                self.tree.selectionModel().select(
                    index[0], QtCore.QItemSelectionModel.Select)

    def _create_gl(self, gui_scale: float):
        from .scene import SampleController
        self.controller = SampleController(self.root, self._scene_selected)
        import glglue.pyside6
        self.glwidget = glglue.pyside6.Widget(
            self, self.controller, dpi_scale=gui_scale)
        return self.glwidget

    @property
    def humanoid_scene(self):
        return self.controller.scene

    def _create_dock(self, area, name, widget):
        dock = QtWidgets.QDockWidget(name, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        self.view_menu.addAction(dock.toggleViewAction())
        self.docks[area] = dock

    def _on_selected(self, selected):
        self.humanoid_scene.selected = None
        selected = selected.indexes()
        if not selected:
            return
        item = selected[0].internalPointer()
        if not isinstance(item, humanoid.Bone):
            return

        self.humanoid_scene.selected = item
        self.prop.set_bone(item)
        self.glwidget.update()
