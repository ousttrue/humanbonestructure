from abc import ABCMeta,     abstractmethod


class Scene(metaclass=ABCMeta):
    @abstractmethod
    def draw(self, projection, view):
        pass
