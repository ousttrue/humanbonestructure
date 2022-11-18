import glm


class Plain:
    def __init__(self, normal: glm.vec3, a: glm.vec3) -> None:
        self.normal = glm.normalize(normal)
        self.a = a

    def project(self, p: glm.vec3) -> glm.vec3:
        ap = p - self.a
        n = self.normal
        return p - glm.dot(n, ap) * n
