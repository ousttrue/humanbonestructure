from typing import TypedDict
import glm


class Coordinate(TypedDict):
    yaw: glm.vec3
    pitch: glm.vec3
    roll: glm.vec3
