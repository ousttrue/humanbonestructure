from .panel_base import *
from ...formats.humanoid_bones import HumanoidBone


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
            case (HumanoidBone.hips
                  | HumanoidBone.spine
                  | HumanoidBone.chest
                  | HumanoidBone.neck
                  | HumanoidBone.head
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
            case (HumanoidBone.leftUpperLeg
                  | HumanoidBone.leftLowerLeg
                  | HumanoidBone.leftFoot
                  | HumanoidBone.leftToes
                  | HumanoidBone.rightUpperLeg
                  | HumanoidBone.rightLowerLeg
                  | HumanoidBone.rightFoot
                  | HumanoidBone.rightToes
                  ):
                return True
        return False
