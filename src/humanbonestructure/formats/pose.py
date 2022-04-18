from typing import NamedTuple, Optional, List, Dict, Set
import abc
from .transform import Transform
from .humanoid_bones import HumanoidBone, HumanoidBodyParts


class BonePose(NamedTuple):
    name: str
    humanoid_bone: Optional[HumanoidBone]
    transform: Transform


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


class Motion(abc.ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    def get_humanbones(self) -> Set[HumanoidBone]:
        return set()

    @abc.abstractmethod
    def get_current_pose(self) -> Pose:
        raise NotImplementedError()


class Empty(Motion):
    def __init__(self) -> None:
        super().__init__('__empty__')
        self.pose = Pose(self.name)

    def get_current_pose(self) -> Pose:
        return self.pose
