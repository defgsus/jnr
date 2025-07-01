from typing import Optional, List, Tuple, Union, Iterable

import pymunk

from src.graphics import RenderSettings, Style
from src.physics.shapesettings import ShapeSettings


class SpaceObject:

    def __init__(
            self,
            shape_settings: Optional[ShapeSettings] = None,
            style: Optional[Style] = None,
            name: Optional[str] = None,
    ):
        from .space import Space
        self.style: Style = style or Style()
        self.shape_settings: ShapeSettings = shape_settings or ShapeSettings()
        self.name: str = name or self.__class__.__name__
        self.space: Space = None

    def __repr__(self):
        return f"SpaceObject('{self.name}')"

    @property
    def position(self) -> pymunk.Vec2d:
        return pymunk.Vec2d(0, 0)

    def step(self, rs: RenderSettings):
        pass

    def create_graph_objects(self) -> Iterable["GraphObject"]:
        return []

    def add_to_space(self):
        raise NotImplementedError
