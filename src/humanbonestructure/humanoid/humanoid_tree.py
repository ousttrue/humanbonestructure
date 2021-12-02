from PySide6 import QtCore
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
