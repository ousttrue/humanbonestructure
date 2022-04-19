from typing import NamedTuple, Tuple
import glm


class Transform(NamedTuple):
    translation: glm.vec3
    rotation: glm.quat
    scale: glm.scale

    @staticmethod
    def identity() -> 'Transform':
        return Transform(glm.vec3(0), glm.quat(), glm.vec3(1))

    @staticmethod
    def from_translation(t: glm.vec3) -> 'Transform':
        return Transform(t, glm.quat(), glm.vec3(1))

    def __str__(self) -> str:
        if self.translation == (0, 0, 0):
            return f'r[{self.rotation}]'
        else:
            return f't[{self.translation}], r[{self.rotation}]'

    def reverse_z(self) -> 'Transform':
        axis = glm.axis(self.rotation)
        angle = glm.angle(self.rotation)
        return Transform(
            glm.vec3(self.translation.x,
                     self.translation.y, -self.translation.z),
            glm.angleAxis(-angle, glm.vec3(axis.x, axis.y, -axis.z)),
            self.scale
        )
