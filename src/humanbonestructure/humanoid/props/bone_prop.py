from PySide6 import QtWidgets, QtCore
from .panels import BodyPanel, LegPanel
from .. import humanoid


class BoneProp(QtWidgets.QWidget):
    value_changed = QtCore.Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.box_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.box_layout)
        self.bone_label = QtWidgets.QLabel()
        self.box_layout.addWidget(self.bone_label)

        self.current = None
        self.parts = [
            BodyPanel(self),
            LegPanel(self),
        ]

        for p in self.parts:
            p.setHidden(True)
            p.value_changed.connect(self.value_changed)  # type: ignore

    def set_bone(self, bone: humanoid.Bone):
        if self.current:
            self.current.setHidden(True)
            self.box_layout.removeWidget(self.current)

        for p in self.parts:
            if p.is_match(bone):
                self.box_layout.addWidget(p)
                self.current = p
                self.current.setHidden(False)
                self.current.set_bone(bone)
                break
