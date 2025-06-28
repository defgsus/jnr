from typing import List, Tuple, Optional, Union

import pymunk
import numpy as np

from src.graphics import RenderSettings, TiledTileset
from .space import Space
from .spaceobject import SpaceObject
from ..graphics.style import Style


class Polygon(SpaceObject):

    def __init__(
            self,
            vertices: List[Tuple[float, float]],
            static: bool = False,
            position: Tuple[float, float] = (0, 0),
            style: Optional[Style] = None,
    ):
        super().__init__()
        self.vertices = vertices
        self.static = static
        self.initial_position = position
        self.style = style

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position / Space.S

    def add_to_space(self, space: pymunk.Space):
        self.space = space

        mass = 1
        self.body = pymunk.Body(
            #mass=mass,
            #moment=pymunk.moment_for_poly(mass, self.vertices, (0, 0)),
            body_type=pymunk.Body.STATIC if self.static else pymunk.Body.DYNAMIC,
        )
        self.body.position = pymunk.Vec2d(*self.initial_position) * Space.S
        shape = pymunk.Poly(self.body, [(Space.S * v[0], Space.S * v[1]) for v in self.vertices])
        shape.friction = 1.
        shape.density = 3
        shape.mass = mass

        self.space.add(self.body, shape)

    def step(self, rs: RenderSettings):
        pass #print(self.__class__.__name__, self.body.position)

    def create_graph_object(self):
        from ..graphics.polygonrender import PolygonRender
        return PolygonRender(self, style=self.style)
