from ..gui.selector import TableSelector
from ..gui.motion_list import MotionList
from ..formats.pose import Motion
from .motion_list import MotionList


class MotionSelector(TableSelector[Motion]):
    def __init__(self) -> None:
        from .pose_generator import PoseGenerator
        self.pose_generator = PoseGenerator()
        self.motion_list = MotionList()
        super().__init__('pose selector', self.motion_list, self.motion_list._filter.show)
        self.selected += self.pose_generator.set_motion
