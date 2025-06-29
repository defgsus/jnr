from typing import List, Tuple, Optional, Union

import pymunk
import numpy as np

from src.graphics import RenderSettings, Style
from .shapesettings import ShapeSettings
from .space import Space
from .spaceobject import SpaceObject


class Circle(SpaceObject):

    def __init__(
            self,
            radius: float,
            position: Tuple[float, float] = (0, 0),
            shape_settings: Optional[ShapeSettings] = None,
            style: Optional[Style] = None,
            name: Optional[str] = None,
    ):
        super().__init__(name=name, style=style, shape_settings=shape_settings)
        self.radius = radius
        self.initial_position = position

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position / Space.S

    def add_to_space(self):
        self.body = pymunk.Body(
            body_type=pymunk.Body.STATIC if self.shape_settings.static else pymunk.Body.DYNAMIC,
        )
        self.body.position = pymunk.Vec2d(*self.initial_position) * Space.S
        shape = pymunk.Circle(self.body, self.radius * Space.S)
        self.shape_settings.apply_to_shape(shape)

        self.space.space.add(self.body, shape)

    def step(self, rs: RenderSettings):
        pass

    def create_graph_objects(self):
        from ..graphics.polygonrender import PolygonRender
        yield PolygonRender(self)
