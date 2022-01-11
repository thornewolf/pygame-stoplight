from dataclasses import dataclass
from utils import DeltaPosition, Direction, Position


@dataclass
class StoplightSettings:
    width: float
    height: float


class Stoplight:
    def __init__(self, location: Position, settings: StoplightSettings) -> None:
        self.settings = settings
        self.position: Position = location
        self._dir_tick = 0
        self._allowed_directions_options = (
            [Direction.LEFT, Direction.RIGHT],
            [Direction.UP, Direction.DOWN]
        )

    def __repr__(self) -> str:
        return f"Stoplight[{self.position=}, {self.allowed_directions=}]"

    @property
    def allowed_directions(self) -> list[Direction]:
        return self._allowed_directions_options[self._dir_tick % len(self._allowed_directions_options)]

    def toggle_direction(self) -> None:
        # TODO: Some logic specific to the stoplight to support multiple "types" of stoplight
        self._dir_tick += 1

    def car_allowed_in(self, position: "Position", from_direction: Direction) -> bool:
        diff = position - self.position
        assert isinstance(diff, DeltaPosition)

        if abs(diff.dx) >= self.settings.width / 2 or abs(diff.dy) >= self.settings.height / 2:
            return True

        match from_direction:
            case Direction.LEFT | Direction.RIGHT:
                if abs(diff.dx) >= self.settings.width / 2:
                    return True
                if from_direction not in self.allowed_directions:
                    return False
            case Direction.UP | Direction.DOWN:
                if abs(diff.dy) >= self.settings.height / 2:
                    return True
                if from_direction not in self.allowed_directions:
                    return False

        return True
