from typing import List, Tuple, Optional, Union

import pymunk
import numpy as np

from src.graphics import RenderSettings
from .space import Space
from .spaceobject import SpaceObject


class Circle(SpaceObject):

    def __init__(
            self,
            radius: float,
            static: bool = False,
            position: Tuple[float, float] = (0, 0),
    ):
        super().__init__()
        self.radius = radius
        self.static = static
        self.initial_position = position

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position / Space.S

    def add_to_space(self, space: pymunk.Space):
        self.space = space

        mass = 1
        self.body = pymunk.Body(
            body_type=pymunk.Body.STATIC if self.static else pymunk.Body.DYNAMIC,
        )
        self.body.position = pymunk.Vec2d(*self.initial_position) * Space.S
        shape = pymunk.Circle(self.body, self.radius * Space.S)
        shape.friction = 1.
        shape.density = 3
        shape.mass = mass

        self.space.add(self.body, shape)

    def step(self, rs: RenderSettings):
        pass

    def create_graph_object(self):
        from ..graphics.polygonrender import PolygonRender
        return PolygonRender(self)
