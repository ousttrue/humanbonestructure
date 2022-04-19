from typing import TypeVar, Generic, Callable, List, Optional

T = TypeVar('T')


class EventProperty(Generic[T]):
    def __init__(self, default_value: T) -> None:
        super().__init__()
        self.callbacks: List[Callable[[T], None]] = []
        if default_value:
            self.value = default_value
        else:
            self.value = None

    def __iadd__(self, callback: Callable[[T], None]):
        self.callbacks.append(callback)
        return self

    def set(self, value: T):
        self.value = value

        self.fire()

    def fire(self):
        value = self.value
        for callback in self.callbacks:
            callback(value)  # type: ignore

    def get(self) -> T:
        assert self.value
        return self.value


class OptionalEventProperty(Generic[T]):
    def __init__(self, default_value: Optional[T] = None) -> None:
        super().__init__()
        self.callbacks: List[Callable[[T], None]] = []
        if default_value:
            self.value = default_value
        else:
            self.value = None

    def __iadd__(self, callback: Callable[[Optional[T]], None]):
        self.callbacks.append(callback)
        return self

    def set(self, value: T):
        self.value = value

        self.fire()

    def fire(self):
        value = self.value
        for callback in self.callbacks:
            callback(value)  # type: ignore

    def get(self) -> T:
        assert self.value
        return self.value
