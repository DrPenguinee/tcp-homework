import enum


class TimeoutState(enum.Enum):
    default = 1
    increased = 4
    maximum = 20


class Timeout:
    def __init__(self, default: float):
        self.default = default
        self.value = default
        self.state = TimeoutState.default

    def inc(self) -> float:
        if self.state == TimeoutState.default:
            self.state = TimeoutState.increased
        elif self.state == TimeoutState.increased:
            self.state = TimeoutState.maximum
        self.value = self.default * self.state.value
        return self.value

    def reset(self) -> float:
        self.state = TimeoutState.default
        self.value = self.default
        return self.value

    def maximum(self) -> float:
        return self.default * self.state.maximum.value
