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


class BodyPanel(QtWidgets.QWidget):
    '''
    Hips, Spine, Chest, Neck Head

       Y
       ^
       |
       +->X
      /
     L
    Z

    主: X+ 前屈
    副: Z+ 右屈
    捩: Y+ 左に捩じる
    '''

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.box_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.box_layout)

        self.label = QtWidgets.QLabel()
        self.label.setText("Hips, Spine, Chest, Neck Head")
        self.box_layout.addWidget(self.label)

        slider, layout = self._label_slider("前後屈")
        self.main_slider = slider
        self.box_layout.addLayout(layout)

        slider, layout = self._label_slider("右左屈")
        self.sub_slider = slider
        self.box_layout.addLayout(layout)

        slider, layout = self._label_slider("左右捩")
        self.roll_slider = slider
        self.box_layout.addLayout(layout)

    def _label_slider(self, text: str):
        layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel(self)
        label.setText(text)
        layout.addWidget(label)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        slider.setMinimum(-180)
        slider.setMaximum(180)
        layout.addWidget(slider)
        return slider, layout

    def is_match(self, bone: humanoid.Bone) -> bool:
        match bone.bone:
            case (humanoid.HumanBones.Hips
                  | humanoid.HumanBones.Spine
                  | humanoid.HumanBones.Chest
                  | humanoid.HumanBones.Neck
                  | humanoid.HumanBones.Head
                  ):
                return True
        return False


class BoneProp(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.box_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.box_layout)
        self.bone_label = QtWidgets.QLabel()
        self.box_layout.addWidget(self.bone_label)

        self.current = None
        self.parts = [
            BodyPanel(self)
        ]
        for p in self.parts:
            p.setHidden(True)

    def set_bone(self, bone: humanoid.Bone):
        if self.current:
            self.current.setHidden(True)
            self.box_layout.removeWidget(self.current)

        for p in self.parts:
            if p.is_match(bone):
                self.box_layout.addWidget(p)
                self.current = p
                self.current.setHidden(False)
                break


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, gui_scale: float = 1.0):
        super().__init__()
        self.setWindowTitle('humanoid view')
        menu = self.menuBar()
        view_menu = menu.addMenu("&View")
        self.view_menu = menu.addMenu("&File")
        self.docks = {}
        self.root = humanoid.make_humanoid(1.0)

        self._create_tree()
        self._create_gl(gui_scale)
        self.prop = BoneProp(self)

        self.setCentralWidget(self.tree)
        self._create_dock(QtCore.Qt.LeftDockWidgetArea, "view", self.glwidget)
        self._create_dock(QtCore.Qt.RightDockWidgetArea, "prop", self.prop)

    def _create_tree(self):
        self.tree = QtWidgets.QTreeView()

        # add_root
        root = humanoid.Bone(humanoid.HumanBones.EndSite,
                             humanoid.Float3(0, 0, 0), [self.root])
        self.model = HumanoidTreeModel(root)
        self.tree.setModel(self.model)
        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)

        self.tree.selectionModel().selectionChanged.connect(  # type: ignore
            self._on_selected)

        return self.tree

    def _create_gl(self, gui_scale: float):
        import glglue.pyside6
        import glglue.gl3.samplecontroller
        self.controller = glglue.gl3.samplecontroller.SampleController()
        self.humanoid_scene = humanoid_scene.HumanoidScene(
            self.root)
        self.controller.scene = self.humanoid_scene
        self.glwidget = glglue.pyside6.Widget(
            self, self.controller, dpi_scale=gui_scale)
        return self.glwidget

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
