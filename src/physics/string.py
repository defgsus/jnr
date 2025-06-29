from typing import List, Tuple, Optional, Union

import pymunk
import numpy as np

from src.graphics.rendersettings import RenderSettings
from .space import Space
from .spaceobject import SpaceObject
from ..graphics.style import Style


class String(SpaceObject):

    def __init__(
            self,
            positions: Union[List[List[float]], np.ndarray],
            style: Optional[Style] = None,
    ):
        super().__init__()
        self.init_positions = positions
        self.style = style
        self.bodies: List[pymunk.Body] = []
        self.shapes: List[pymunk.Shape] = []

    def add_to_space(self, space: pymunk.Space):
        self.space = space

        mass = 1
        for pos in self.init_positions:
            body = pymunk.Body()
            body.position = pymunk.Vec2d(*pos) * Space.S
            shape = pymunk.Circle(body, radius=0.01)
            shape.friction = 1.
            shape.density = 1
            shape.mass = mass
            self.bodies.append(body)
            self.shapes.append(shape)

        constraints = [
            pymunk.PinJoint()
        ]
        for body, next_body in zip(self.bodies, self.bodies[1:]):
            con = pymunk.DampedSpring(
                body, next_body,
                (0, 0), (0, 0),
                rest_length=body.position.get_distance(next_body.position),
            )
            constraints.append(con)

        self.space.add(*self.bodies, *self.shapes, *constraints)

    def step(self, rs: RenderSettings):
        pass #print(self.__class__.__name__, self.body.position)

    #def create_graph_object(self):
        #from ..graphics.polygonrender import PolygonRender
        #return PolygonRender(self, style=self.style)
