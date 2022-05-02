from typing import TypeVar, Generic, Callable, List, Optional

T = TypeVar('T')


class Event():
    def __init__(self) -> None:
        super().__init__()
        self.callbacks: List[Callable[[], None]] = []

    def __iadd__(self, callback: Callable[[], None]):
        self.callbacks.append(callback)
        return self

    def fire(self):
        for callback in self.callbacks:
            callback()


class EventProperty(Generic[T]):
    def __init__(self, default_value: T) -> None:
        super().__init__()
        self.callbacks: List[Callable[[T], None]] = []
        self.value = default_value

    def __iadd__(self, callback: Callable[[T], None]):
        self.callbacks.append(callback)
        return self

    def set(self, value: T):
        self.value = value

        self.fire()

    def fire(self):
        value = self.value
        for callback in self.callbacks:
            callback(value)

    def get(self) -> T:
        assert self.value
        return self.value


class OptionalEventProperty(Generic[T]):
    def __init__(self, default_value: Optional[T] = None) -> None:
        super().__init__()
        self.callbacks: List[Callable[[Optional[T]], None]] = []
        self.value = default_value

    def __iadd__(self, callback: Callable[[Optional[T]], None]):
        self.callbacks.append(callback)
        return self

    def set(self, value: Optional[T]):
        self.value = value

        self.fire()

    def fire(self):
        value = self.value
        for callback in self.callbacks:
            callback(value)

    def get(self) -> T:
        assert self.value
        return self.value
