import numpy as np
import pymunk

from .shapesettings import ShapeSettings
from .spaceobject import *
from .polygon import Polygon

import pygame

from ..graphics import Style
from ..timings import ValueScheduler, TimeThreshold
from .space import Space


class Player(Polygon):

    def __init__(
            self,
            position: Tuple[float, float] = (0, 0),
    ):
        h = .7
        w = h * 20 / 50
        super().__init__(
            vertices=[(-w, -h), (w, -h), (w, h), (-w, h)],
            #vertices=[
            #    (np.sin(t) * h, np.cos(t) * h)
            #    for t in np.linspace(0, np.pi*2, 10)
            #],
            name="player",
            position=position,
            style=Style(
                tileset_filename="character-hero-ars-notoria-8x4-46x50.tsx",
                # show_rotation=False,
                scale=pymunk.Vec2d(50/20, 1.) * 1.1,
            ),
            shape_settings=ShapeSettings(
                friction=10.,
                mass=1,
                density=10,
                filter=pymunk.ShapeFilter(
                    categories=Space.CAT_PLAYER,
                    mask=pymunk.ShapeFilter.ALL_MASKS(),
                )
            ),
        )
        self.sprite_select = ValueScheduler("stand")
        self.jump_threshold = TimeThreshold(max_seconds_active=.2)
        self.hit_threshold = TimeThreshold(max_seconds_active=.2)
        self.on_ground: bool = False

    def step(self, rs: RenderSettings):
        world_hit_point = self.body.position + pymunk.Vec2d(.0, -.75) * self.space.S
        result = self.space.space.point_query(
            point=world_hit_point,
            max_distance=.1 * self.space.S,
            shape_filter=pymunk.ShapeFilter(
                mask=0b101,
            )
        )
        self.on_ground = bool(result)

        keys = pygame.key.get_pressed()

        if self.jump_threshold.check_key_press(rs, keys[pygame.K_UP]):
            if self.on_ground:
                self.sprite_select.schedule("jump1", 0)
                self.sprite_select.schedule("jump2", 0.5)
                self.body.apply_impulse_at_world_point(
                    (0, 50*self.shape_settings.mass),
                    self.body.position,
                )

        if self.hit_threshold.check_key_press(rs, keys[pygame.K_SPACE]):
            self.sprite_select.schedule("hit1", 0)
            self.sprite_select.schedule("hit2", 0.1)
            self.sprite_select.schedule("hit3", 0.2)
            self.sprite_select.schedule("stand", 0.3)
            self.hit(dir_x=-1 if self.style.tileset_controller.flip_x else 1)

        mapping = {
            # pygame.K_UP: (0, 1),
            pygame.K_DOWN: (0, -1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
        }
        V = 5 * self.shape_settings.mass
        for key, impulse in mapping.items():
            if keys[key]:
                v = V
                if key == pygame.K_LEFT:
                    self.style.tileset_controller.flip_x = True
                if key == pygame.K_RIGHT:
                    self.style.tileset_controller.flip_x = False
                self.body.apply_impulse_at_world_point(
                    (impulse[0]*v, impulse[1]*v),
                    self.body.position,
                )

        self.sprite_select.step(rs)
        sprite = self.sprite_select.value
        if sprite == "stand" and not self.on_ground:
            sprite = "jump2"
        elif "jump" in sprite and self.on_ground:
            sprite = "stand"
        self.style.tileset_controller.set_type(sprite)

        self.body.angular_velocity += rs.dt * self.body.angle * -10
        self.body.angle = max(-.01, min(0.01, self.body.angle))

    def hit(self, dir_x: float):
        world_hit_point = self.body.position + pymunk.Vec2d(dir_x * .3, .0) * self.space.S
        result = self.space.space.point_query(
            point=world_hit_point,
            max_distance=self.space.S,
            shape_filter=pymunk.ShapeFilter(
                mask=0b100,
            )
        )
        if result:
            print("R----"*10)
            for r in result:
                print(r.shape.filter, r.shape)
                r.shape.body.apply_impulse_at_world_point(
                    point=world_hit_point,
                    impulse=(dir_x * 50, 0),
                )

    def create_graph_objects(self):
        from ..graphics.polygonrender import PolygonRender
        yield PolygonRender(self)
        yield from super().create_graph_objects()
