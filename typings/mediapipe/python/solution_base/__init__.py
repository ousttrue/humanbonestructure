from typing import List
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmarkList


class SolutionOutputs:
    multi_hand_landmarks: List[NormalizedLandmarkList]
    ...
