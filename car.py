from dataclasses import dataclass
from typing import Callable
from utils import DeltaPosition, Direction, Position


@dataclass
class CarSettings:
    id: int
    birth_time: int
    speed: float
    length: float


class Car:
    def __init__(
        self,
        settings: CarSettings,
        target_path: list[Position],
        position_validation_callback: Callable[["Car"], bool],
        car_journey_complete_callback: Callable[[int], None],
    ) -> None:
        self.target_path: list[Position] = target_path
        self.path_progress: float = 0
        self.settings = settings
        self.can_be_at_position_callback: Callable[
            ["Car"], bool
        ] = position_validation_callback
        self.journey_complete_callback = car_journey_complete_callback

    @property
    def position(self):
        # TODO: Implement a way to infer x,y position by interpolating on path
        if self.path_progress == 0:
            return self.target_path[0]
        if self.path_progress >= 1:
            return self.target_path[-1]

        f_i = (len(self.target_path) - 1) * self.path_progress
        i, p = divmod(f_i, 1.0)
        i = int(i)

        p1 = self.target_path[i]
        p2 = self.target_path[i + 1]
        dp = p2 - p1
        assert isinstance(dp, DeltaPosition)
        dp = dp * p

        return p1 + dp

    @property
    def delta(self) -> DeltaPosition:
        f_i = (len(self.target_path) - 1) * self.path_progress
        i, _ = divmod(f_i, 1.0)
        i = int(i)

        try:
            d = self.target_path[i + 1] - self.target_path[i]
        except:
            d = self.target_path[-1] - self.target_path[-2]

        assert isinstance(d, DeltaPosition)
        return d

    @property
    def direction_from(self):
        p1 = self.position
        self.path_progress += self.settings.speed * 1 / 30
        p2 = self.position
        self.path_progress -= self.settings.speed * 1 / 30

        dp = p2 - p1
        assert isinstance(dp, DeltaPosition)
        if abs(dp.dx) > abs(dp.dy):
            if dp.dx < 0:
                return Direction.RIGHT
            return Direction.LEFT
        else:
            if dp.dy < 0:
                return Direction.DOWN
            return Direction.UP

    def maybe_step_position(self, dt: float) -> None:
        # TODO: Update position to new location only if car is allowed there. (collision check)
        delta_progress = self.settings.speed * dt
        self.path_progress += delta_progress
        if not self.can_be_at_position_callback(self):
            self.path_progress -= delta_progress

        if self.path_progress >= 1:
            self.journey_complete_callback(self.settings.id)

    def __repr__(self) -> str:
        return f"Car[{self.path_progress=}, {self.position=}, {self.direction_from=}]"
