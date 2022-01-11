import pygame
import numpy as np
import random
import time
from dataclasses import dataclass


from car import Car, CarSettings
from stoplight import Stoplight, StoplightSettings
from utils import DeltaPosition, Direction, Position


@dataclass
class GameDimensions:
    width: int
    height: int


@dataclass
class GameConfig:
    dimensions: GameDimensions
    ticks_per_second: int

    @property
    def dt(self):
        return 1 / self.ticks_per_second


class GameStateTracker:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.score = 0
        self.max_ticks_before_death = 300

    @property
    def ticks_left(self):
        m = float("inf")
        for c in self.game.cars.values():
            m = min(m, c.settings.birth_time)
        if m == float("inf"):
            m = self.max_ticks_before_death
        left = (
            self.max_ticks_before_death - (self.game.c_tick - m)
        ) / self.max_ticks_before_death
        if left < 0:
            self.game.game_over = True
        return left


class Game:
    def __init__(self, config: GameConfig) -> None:
        self.config = config
        self.tracker = GameStateTracker(self)
        self.reset()

        self.cars: dict[int, Car] = {}
        self.lights: list[Stoplight] = [
            Stoplight(Position(615, 590), StoplightSettings(350, 350)),
        ]

        self.last_added_tick = -1000
        self.c_tick = 0

        self.add_car()

    def reset(self):
        self.car_count = 0
        self.game_over = False

    def add_car(self):
        self.car_count += 1
        path = random.choice(
            (
                [Position(1500, 550), Position(-200, 550)],
                [Position(670, 1500), Position(670, -220)],
            )
        )
        speed = 0.4 * np.log10(10 + self.c_tick / 50)
        print(speed)
        c = Car(
            CarSettings(self.car_count, self.c_tick, speed, 150),
            path,
            self.car_can_be_at_position,
            self.remove_car,
        )
        self.cars[self.car_count] = c

    def remove_car(self, id: int):
        print(f"die {id}")
        self.tracker.score += 1
        del self.cars[id]

    def car_can_be_at_position(self, car: Car) -> bool:
        for light in self.lights:
            if not light.car_allowed_in(car.position, car.direction_from):
                return False

        for other_car in self.cars.values():
            if car is other_car:
                continue
            delta = other_car.position - car.position
            assert isinstance(delta, DeltaPosition)
            if delta < car.settings.length * 0.6:
                return False
        return True

    def tick(self):
        self.c_tick += 1
        if self.c_tick > self.last_added_tick + 50 / (self.c_tick / 500):
            self.add_car()
            self.last_added_tick = self.c_tick

        keys = list(self.cars.keys())
        for key in keys:
            car = self.cars[key]
            car.maybe_step_position(self.config.dt)
        for light in self.lights:
            light  # holy


class GameGui:
    def __init__(self, game: Game) -> None:
        pygame.font.init()
        self.game = game

    def draw_img_centered_at(
        self, screen: pygame.surface.Surface, img: pygame.surface.Surface, pos: Position
    ):
        r = img.get_rect()
        r.center = pos.tuple
        screen.blit(img, r)

    def draw_game_elements(self, screen: pygame.surface.Surface) -> None:
        screen.blit(pygame.image.load("assets/4wayintersection.png"), (0, 0))

        bar = pygame.image.load("assets/Bar.png")
        bar = pygame.transform.scale(bar, (100 * self.game.tracker.ticks_left, 20))
        screen.blit(bar, (200, 200))
        font = pygame.font.Font("freesansbold.ttf", 32)
        text = font.render(f"Score: {self.game.tracker.score}", True, (0, 0, 0))
        screen.blit(text, (200, 250))

        for car in self.game.cars.values():
            img = pygame.image.load("assets/car1.png")
            rot = np.arctan2(car.delta.dx, car.delta.dy) * 180 / np.pi + 90
            img = pygame.transform.rotate(img, rot)
            self.draw_img_centered_at(screen, img, car.position)
        for light in self.game.lights:
            img_name = (
                "light1"
                if light.allowed_directions == [Direction.LEFT, Direction.RIGHT]
                else "light2"
            )
            img = pygame.image.load(f"assets/{img_name}.png")
            self.draw_img_centered_at(screen, img, light.position)

    def play(self):
        screen = pygame.display.set_mode(
            (self.game.config.dimensions.width, self.game.config.dimensions.height)
        )

        dt = self.game.config.dt
        g = self.game

        pt = 0
        running = True
        while running and not g.game_over:
            ct = time.time()
            if ct - pt < dt:
                continue
            pt = ct

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game.lights[0].toggle_direction()
                    if event.key == pygame.K_0:
                        self.game.lights[1].toggle_direction()

            g.tick()

            # draw
            screen.fill((0, 0, 0))
            self.draw_game_elements(screen)
            pygame.display.flip()

            if g.game_over:
                break
