import math
from typing import Optional
from PySide6 import QtWidgets, QtCore
from .. import humanoid


MAX_VALUE = 1024
TO_RADIAN = math.pi/180


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

    value_changed = QtCore.Signal()

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.box_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.box_layout)

        self.label = QtWidgets.QLabel()
        self.label.setText("Hips, Spine, Chest, Neck Head")
        self.box_layout.addWidget(self.label)

        slider, layout = self._label_slider("前後屈")
        self.main_slider = slider
        self.bone: Optional[humanoid.Bone] = None

        def on_main(value):
            if self.bone:
                self.bone.local_rotation_main = value / MAX_VALUE * math.pi
                self.value_changed.emit()  # type: ignore
        self.main_slider.valueChanged.connect(on_main)  # type: ignore
        self.box_layout.addLayout(layout)

        slider, layout = self._label_slider("右左屈")
        self.sub_slider = slider

        def on_sub(value):
            if self.bone:
                self.bone.local_rotation_sub = value / MAX_VALUE * math.pi
                self.value_changed.emit()  # type: ignore
        self.sub_slider.valueChanged.connect(on_sub)  # type: ignore
        self.box_layout.addLayout(layout)

        slider, layout = self._label_slider("左右捩")
        self.roll_slider = slider

        def on_roll(value):
            if self.bone:
                self.bone.local_rotation_roll = value / MAX_VALUE * math.pi
                self.value_changed.emit()  # type: ignore
        self.roll_slider.valueChanged.connect(on_roll)  # type: ignore
        self.box_layout.addLayout(layout)

    def _label_slider(self, text: str):
        layout = QtWidgets.QHBoxLayout()

        label = QtWidgets.QLabel(self)
        label.setText(text)
        layout.addWidget(label)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        slider.setRange(-MAX_VALUE, MAX_VALUE)

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

    def set_bone(self, bone: humanoid.Bone):
        self.bone = bone
        self.main_slider.setValue(self.bone.local_rotation_main)
        self.sub_slider.setValue(self.bone.local_rotation_sub)
        self.roll_slider.setValue(self.bone.local_rotation_roll)
