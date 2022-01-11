from enum import Enum
import typing


class Direction(Enum):
    NULL = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class LightState(Enum):
    NULL = 0
    GREEN = 1
    RED = 2


class DeltaPosition:
    def __init__(self, dx: float, dy: float) -> None:
        self.dx = dx
        self.dy = dy

    def __lt__(self, other: float) -> bool:
        return (self.dx ** 2 + self.dy ** 2) ** 0.5 < other

    def __gt__(self, other: float) -> bool:
        return (self.dx ** 2 + self.dy ** 2) ** 0.5 > other

    def __repr__(self) -> str:
        return f"DeltaPosition[{self.dx=} {self.dy=}]"

    def __mul__(self, other: float) -> "DeltaPosition":
        return DeltaPosition(self.dx * other, self.dy * other)


class Position:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Position[{self.x}, {self.y}]"

    def __sub__(
        self, other: typing.Union["Position", "DeltaPosition"]
    ) -> typing.Union["DeltaPosition", "Position"]:
        if isinstance(other, Position):
            return DeltaPosition(self.x - other.x, self.y - other.y)
        else:
            return Position(self.x + other.dx, self.y + other.dy)

    def __add__(self, other: DeltaPosition) -> "Position":
        return Position(self.x + other.dx, self.y + other.dy)

    @property
    def tuple(self):
        return (int(self.x), int(self.y))
