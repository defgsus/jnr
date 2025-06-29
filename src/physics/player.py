from .spaceobject import *
from .polygon import Polygon

import pygame

from ..graphics import Style
from ..timings import ValueScheduler, TimeThreshold


class Player(Polygon):

    def __init__(
            self,
            position: Tuple[float, float] = (0, 0),
    ):
        h = .7
        w = h * 46 / 50
        super().__init__(
            vertices=[(-w, -h), (w, -h), (w, h), (-w, h)],
            position=position,
            style=Style(tileset_filename="character-hero-ars-notoria-8x4-46x50.tsx"),
        )
        self.sprite_select = ValueScheduler("stand")
        self.jump_threshold = TimeThreshold(max_seconds_active=.2)
        self.hit_threshold = TimeThreshold(max_seconds_active=.2)

    def step(self, rs: RenderSettings):
        keys = pygame.key.get_pressed()

        self.jump_threshold.step(rs)
        self.jump_threshold.set_active(rs, keys[pygame.K_UP])
        if self.jump_threshold.active:
            self.body.apply_impulse_at_world_point(
                (0, 10),
                self.body.position,
            )

        self.hit_threshold.step(rs)
        self.hit_threshold.set_active(rs, keys[pygame.K_SPACE])
        if self.hit_threshold.active:
            self.sprite_select.schedule("hit1", 0)
            self.sprite_select.schedule("hit2", 0.1)
            self.sprite_select.schedule("hit3", 0.2)
            self.sprite_select.schedule("stand", 0.3)

        mapping = {
            # pygame.K_UP: (0, 1),
            pygame.K_DOWN: (0, -1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
        }
        V = 5
        for key, impulse in mapping.items():
            if keys[key]:
                v = V
                if key == pygame.K_UP:
                    v *= 2
                if key == pygame.K_LEFT:
                    self.style.tileset_controller.flip_x = True
                if key == pygame.K_RIGHT:
                    self.style.tileset_controller.flip_x = False
                self.body.apply_impulse_at_world_point(
                    (impulse[0]*v, impulse[1]*v),
                    self.body.position,
                )

        self.sprite_select.step(rs)
        self.style.tileset_controller.set_type(self.sprite_select.value)
        self.body.angular_velocity += rs.dt * self.body.angle * -10
