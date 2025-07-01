import math
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
            way_points: Optional[List[Tuple[float, float]]] = None,
            way_speed: float = 1.,  # N cells/second
            way_offset: float = 0.,
    ):
        super().__init__(name=name, shape_settings=shape_settings, style=style)
        self.vertices = vertices
        self.initial_position = position
        if way_points:
            way_points = [pymunk.Vec2d(*p) for p in way_points]
        self.way_points: Optional[List[pymunk.Vec2d]] = way_points
        self.way_points_index: float = way_offset * len(self.way_points or [])
        self.way_speed = way_speed

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position / Space.S

    def add_to_space(self):
        self.body = pymunk.Body(
            body_type=self.shape_settings.body_type,
        )
        self.body.position = pymunk.Vec2d(*self.initial_position) * Space.S
        self.shape = pymunk.Poly(self.body, [(Space.S * v[0], Space.S * v[1]) for v in self.vertices])
        self.shape_settings.apply_to_shape(self.shape)

        self.space.space.add(self.body, self.shape)

    def step(self, rs: RenderSettings):
        S = Space.S
        if self.way_points:
            cur_point = int(self.way_points_index)
            next_point = self.way_points[(cur_point + 1) % len(self.way_points)] * S
            cur_point = self.way_points[cur_point] * S
            dist = cur_point.get_distance(next_point)

            mix = self.way_points_index - math.floor(self.way_points_index)
            self.body.position = cur_point * (1. - mix) + mix * next_point

            speed = rs.dt / dist * self.way_speed * S
            self.way_points_index = (self.way_points_index + speed) % len(self.way_points)

    def create_graph_objects(self):
        from ..graphics.polygonrender import PolygonRender
        yield PolygonRender(self, style=self.style)
