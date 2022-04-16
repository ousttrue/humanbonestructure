from typing import TypeVar, Generic, Callable, List

T = TypeVar('T')


class EventProperty(Generic[T]):
    def __init__(self, default_value: T, *, show=None) -> None:
        super().__init__()
        self.callbacks: List[Callable[[T], None]] = []
        self.value = default_value
        self.show = show

    def __iadd__(self, callback: Callable[[T], None]):
        self.callbacks.append(callback)
        return self

    def set(self, value: T):
        if self.value == value:
            return
        self.value = value

        self.fire()

    def fire(self):
        value = self.value
        for callback in self.callbacks:
            callback(value)

    def get(self) -> T:
        return self.value
