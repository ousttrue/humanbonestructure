'''
標準T-Poseとそれに対する、ポーズ表現を作ってみる。
'''

from PySide6 import QtCore, QtWidgets, QtGui
from enum import Enum, auto
from typing import NamedTuple, List
from dataclasses import dataclass


class HumanBones(Enum):
    EndSite = auto()
    Hips = auto()
    Spine = auto()
    Chest = auto()
    Neck = auto()
    Head = auto()

    LeftShoulder = auto()
    LeftUpperArm = auto()
    LeftLowerArm = auto()
    LeftHand = auto()

    RightShoulder = auto()
    RightUpperArm = auto()
    RightLowerArm = auto()
    RightHand = auto()

    LeftUpperLeg = auto()
    LeftLowerLeg = auto()
    LeftFoot = auto()
    LeftToes = auto()

    RightUpperLeg = auto()
    RightLowerLeg = auto()
    RightFoot = auto()
    RightToes = auto()


class Float3(NamedTuple):
    x: float
    y: float
    z: float


@dataclass
class Bone:
    bone: HumanBones
    offset: Float3
    children: List['Bone']

    def traverse(self):
        yield self
        for child in self.children:
            for x in child.traverse():
                yield x


def make_humanoid(hips_pos: float) -> Bone:
    head_len = hips_pos / 5
    neck_len = hips_pos / 5
    chest_len = hips_pos / 5
    spine_len = hips_pos / 5
    hips_len = hips_pos / 5
    return Bone(HumanBones.Hips, Float3(0, hips_pos, 0), [
        Bone(HumanBones.Spine, Float3(0, hips_len, 0), [
                Bone(HumanBones.Chest, Float3(0, spine_len, 0), [
                    Bone(HumanBones.Neck, Float3(0, chest_len, 0), [
                        Bone(HumanBones.Head, Float3(0, neck_len, 0), [
                            Bone(HumanBones.EndSite, Float3(0, head_len, 0), [])
                        ])
                    ])
                ])
                ])
    ])


class HumanoidTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, root: Bone):
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
                return str(item.bone)


class HumanoidWiget(QtWidgets.QTabWidget):
    '''
    +----+----+
    |tree|    |
    +----+view|
    |prop|    |
    +----+----+
    '''

    def __init__(self, parent):
        super().__init__(parent)
        self.root = make_humanoid(1.0)

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.tree = QtWidgets.QTreeView()
        self.model = HumanoidTreeModel(self.root)
        self.tree.setModel(self.model)
        layout.addWidget(self.tree)
        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)
