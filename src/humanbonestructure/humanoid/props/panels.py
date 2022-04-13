from .. import humanoid
from .panel_base import *


class BodyPanel(PanelBase):
    '''
    Hips, Spine, Chest, Neck Head

       Y
       ^
       |
       +->X
      /
     L
    Z
    '''

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.label.setText("Hips, Spine, Chest, Neck Head")
        self.x_label.setText("前後屈")
        self.z_label.setText("右左屈")
        self.y_label.setText("左右捩")

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


class LegPanel(PanelBase):
    '''
    UpperLeg, LowerLeg, Foot, Tooes

    X<-+
      /|
     L v
    Z  Y
    '''

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.label.setText("UpperLeg, LowerLeg, Foot, Tooes")
        self.x_label.setText("前後")
        self.z_label.setText("開閉")
        self.y_label.setText("捩り")

    def is_match(self, bone: humanoid.Bone) -> bool:
        match bone.bone:
            case (humanoid.HumanBones.LeftUpperLeg
                  | humanoid.HumanBones.LeftLowerLeg
                  | humanoid.HumanBones.LeftFoot
                  | humanoid.HumanBones.LeftToes
                  | humanoid.HumanBones.RightUpperLeg
                  | humanoid.HumanBones.RightLowerLeg
                  | humanoid.HumanBones.RightFoot
                  | humanoid.HumanBones.RightToes
                  ):
                return True
        return False