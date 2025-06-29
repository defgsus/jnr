from typing import List, Tuple, Optional, Union

import pymunk
import numpy as np

from src.graphics.rendersettings import RenderSettings
from .shapesettings import ShapeSettings
from .space import Space
from .spaceobject import SpaceObject
from ..graphics.style import Style


class Polygon(SpaceObject):

    def __init__(
            self,
            vertices: List[Tuple[float, float]],
            position: Tuple[float, float] = (0, 0),
            shape_settings: Optional[ShapeSettings] = None,
            style: Optional[Style] = None,
            name: Optional[str] = None,
    ):
        super().__init__(name=name, shape_settings=shape_settings, style=style)
        self.vertices = vertices
        self.initial_position = position

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position / Space.S

    def add_to_space(self):
        self.body = pymunk.Body(
            body_type=pymunk.Body.STATIC if self.shape_settings.static else pymunk.Body.DYNAMIC,
        )
        self.body.position = pymunk.Vec2d(*self.initial_position) * Space.S
        shape = pymunk.Poly(self.body, [(Space.S * v[0], Space.S * v[1]) for v in self.vertices])
        self.shape_settings.apply_to_shape(shape)

        self.space.space.add(self.body, shape)

    def step(self, rs: RenderSettings):
        pass #print(self.__class__.__name__, self.body.position)

    def create_graph_objects(self):
        from ..graphics.polygonrender import PolygonRender
        yield PolygonRender(self, style=self.style)
