from typing import NamedTuple, Optional, List, Dict, Set, TypedDict, Tuple
import abc
from .transform import Transform
from .humanoid_bones import HumanoidBone, HumanoidBodyParts


class BonePose(NamedTuple):
    name: str
    humanoid_bone: Optional[HumanoidBone]
    transform: Transform


class BodyRotations(TypedDict):
    hips0: Tuple[float, float, float, float]


class FingerRotations(TypedDict):
    thumb0: Tuple[float, float, float, float]


class JsonPose(TypedDict):
    translationScale: float
    translation: Tuple[float, float, float]
    body: BodyRotations
    leftHand: FingerRotations
    rightHand: FingerRotations


class Pose:
    def __init__(self, name: str):
        self.name = name
        self.bones: List[BonePose] = []
        self._parts: Dict[HumanoidBodyParts, bool] = {
        }

    def get_parts(self, part: HumanoidBodyParts) -> bool:
        value = self._parts.get(part)
        if not isinstance(value, bool):
            def has_part(bone: BonePose) -> bool:
                if not bone.humanoid_bone:
                    return False
                return bone.humanoid_bone.get_part() == part
            value = any(has_part(bone) for bone in self.bones)
            self._parts[part] = value
        return value

    def to_json(self) -> JsonPose:
        return JsonPose()


class Motion(abc.ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self._parts_cache = None

    def get_humanboneparts(self) -> Set[HumanoidBodyParts]:
        if self._parts_cache is None:
            self._parts_cache = set(bone.get_part()
                                    for bone in self.get_humanbones())
        return self._parts_cache

    @abc.abstractmethod
    def get_humanbones(self) -> Set[HumanoidBone]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_current_pose(self) -> Pose:
        raise NotImplementedError()

    def start(self):
        pass

    def stop(self):
        pass


class Empty(Motion):
    def __init__(self) -> None:
        super().__init__('__empty__')
        self.pose = Pose(self.name)

    def get_humanbones(self) -> Set[HumanoidBone]:
        return set()

    def get_current_pose(self) -> Pose:
        return self.pose
