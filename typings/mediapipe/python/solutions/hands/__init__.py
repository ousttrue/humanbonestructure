import numpy
from ...solution_base import SolutionOutputs


class Hands:
    def __init__(self,
                 model_complexity: int,
                 min_detection_confidence: float,
                 min_tracking_confidence: float
                 ) -> None:
        ...

    def __enter__(self) -> 'Hands':
        ...

    def __exit__(self, ex_type, ex_value, trace):
        ...

    def process(self, image: numpy.ndarray) -> SolutionOutputs:
        ...
