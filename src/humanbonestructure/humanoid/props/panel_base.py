import math
from typing import Optional
from PySide6 import QtWidgets, QtCore
from .. import humanoid

MAX_VALUE = 1024
TO_RADIAN = math.pi/180


class PanelBase(QtWidgets.QWidget):
    value_changed = QtCore.Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.box_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.box_layout)

        # label
        self.label = QtWidgets.QLabel()
        self.box_layout.addWidget(self.label)

        # Z
        label, slider, layout = self._label_slider("Z")
        self.z_label = label
        self.z_slider = slider
        self.bone: Optional[humanoid.Bone] = None

        def on_main(value):
            if self.bone:
                self.bone.local_euler.z = value / MAX_VALUE * math.pi
                self.value_changed.emit()  # type: ignore
        self.z_slider.valueChanged.connect(on_main)  # type: ignore
        self.box_layout.addLayout(layout)

        # X
        label, slider, layout = self._label_slider("X")
        self.x_label = label
        self.x_slider = slider

        def on_sub(value):
            if self.bone:
                self.bone.local_euler.x = value / MAX_VALUE * math.pi
                self.value_changed.emit()  # type: ignore
        self.x_slider.valueChanged.connect(on_sub)  # type: ignore
        self.box_layout.addLayout(layout)

        # Y
        label, slider, layout = self._label_slider("Y")
        self.y_label = label
        self.y_slider = slider

        def on_roll(value):
            if self.bone:
                self.bone.local_euler.y = value / MAX_VALUE * math.pi
                self.value_changed.emit()  # type: ignore
        self.y_slider.valueChanged.connect(on_roll)  # type: ignore
        self.box_layout.addLayout(layout)

    def _label_slider(self, text: str):
        layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel(self)
        label.setText(text)
        layout.addWidget(label)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        slider.setRange(-MAX_VALUE, MAX_VALUE)

        layout.addWidget(slider)
        return label, slider, layout

    def is_match(self, bone: humanoid.Bone) -> bool:
        return False

    def set_bone(self, bone: humanoid.Bone):
        self.bone = bone
        self.z_slider.setValue(self.bone.local_euler.x)
        self.x_slider.setValue(self.bone.local_euler.z)
        self.y_slider.setValue(self.bone.local_euler.y)
