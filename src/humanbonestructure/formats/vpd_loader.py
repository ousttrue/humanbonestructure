import re
import glm
from .transform import Transform
from .pmd_loader import SCALING_FACTOR, BONE_HUMANOID_MAP
from .pose import BonePose, Pose, Motion

COMMENT_PATTERN = re.compile(r'(.*?)//.*$')
BONE_NAME_PATTERN = re.compile(r'Bone(\d+)\{(\w+)')


def get_name(open: str) -> str:
    # Bone0{右親指１
    m = BONE_NAME_PATTERN.match(open)
    assert m
    return m.group(2)


def get_t(t: str) -> glm.vec3:
    x, y, z = t[:-1].split(',')
    return glm.vec3(float(x) * SCALING_FACTOR, float(y) * SCALING_FACTOR, float(z) * SCALING_FACTOR)


def get_r(r: str) -> glm.quat:
    x, y, z, w = r[:-1].split(',')
    return glm.quat(float(w), float(x), float(y), float(z))


class Vpd(Motion):
    def __init__(self, name: str):
        self.name = name
        self.pose = Pose(name)

    def __str__(self) -> str:
        return f'<{self.name}:{len(self.pose.bones)}bones>'

    def current_pose(self) -> Pose:
        return self.pose

    @property
    def bones(self):
        return self.pose.bones

    def get_parts(self, part):
        return self.pose.get_parts(part)

    @staticmethod
    def load(data: bytes) -> 'Vpd':
        text = data.decode('cp932', errors='ignore')

        def cleanup_line(src: str) -> str:
            m = COMMENT_PATTERN.match(src)
            if m:
                src = m.group(1)
            return src.strip()

        lines = [l for l in (cleanup_line(l) for l in text.splitlines()) if l]

        l = lines.pop(0)
        if l != 'Vocaloid Pose Data file':
            raise RuntimeError('first line is not "Vocaloid Pose Data file"')

        # target osm ?
        l = lines.pop(0)
        vpd = Vpd(l[:-1])

        m = re.match(r'^(\d+);$', lines.pop(0))
        if not m:
            raise RuntimeError()

        count = int(m.group(1))

        # parse
        for i in range(count):
            open = lines.pop(0)
            t = lines.pop(0)
            assert t[-1] == ';'
            r = lines.pop(0)
            assert r[-1] == ';'
            close = lines.pop(0)
            assert close == '}'

            name = get_name(open)
            humanoid_bone = BONE_HUMANOID_MAP.get(name)
            vpd.pose.bones.append(
                BonePose(name, humanoid_bone, Transform(get_t(t), get_r(r), glm.vec3(1))))

        assert len(vpd.pose.bones) == count

        return vpd
