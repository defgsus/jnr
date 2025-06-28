from typing import Optional, List, Tuple, Union

import pymunk

from src.graphics import RenderSettings


class SpaceObject:

    def __init__(
            self,
    ):
        self.space: Optional[pymunk.Space] = None

    @property
    def position(self) -> pymunk.Vec2d:
        return pymunk.Vec2d(0, 0)

    def step(self, rs: RenderSettings):
        pass

    def create_graph_object(self):
        return None

    def add_to_space(self, space: pymunk.Space):
        raise NotImplementedError






