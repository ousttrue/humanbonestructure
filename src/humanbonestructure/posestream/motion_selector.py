from ..gui.selector import TableSelector


class MotionSelector(TableSelector):
    def __init__(self) -> None:
        from .pose_generator import PoseGenerator
        self.pose_generator = PoseGenerator()
        super().__init__('pose selector',
                         self.pose_generator.motion_list, self.pose_generator.show)
        self.selected += self.pose_generator.set_motion
