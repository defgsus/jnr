from typing import List, Tuple, Optional, Union

import pymunk
import numpy as np

from src.graphics.rendersettings import RenderSettings
from .shapesettings import ShapeSettings
from .space import Space
from .spaceobject import SpaceObject
from ..graphics.style import Style


class String(SpaceObject):

    def __init__(
            self,
            positions: Union[List[List[float]], np.ndarray],
            shape_settings: Optional[ShapeSettings] = None,
            style: Optional[Style] = None,
            name: Optional[str] = None,
    ):
        from src.graphics import MultiSpriteRender

        super().__init__(shape_settings=shape_settings, style=style, name=name)
        self.init_positions = positions
        self.style = style
        self.bodies: List[pymunk.Body] = []
        self.shapes: List[pymunk.Shape] = []
        self.sprite_render: Optional[MultiSpriteRender] = None

    def add_to_space(self):
        for pos in self.init_positions:
            body = pymunk.Body()
            body.position = pymunk.Vec2d(*pos) * Space.S
            shape = pymunk.Circle(body, radius=0.1 * Space.S)
            self.shape_settings.apply_to_shape(shape)
            self.bodies.append(body)
            self.shapes.append(shape)

        query_pos = self.init_positions[0]
        query_pos = pymunk.Vec2d(
            int(query_pos[0]) + .5,
            int(query_pos[1]),
        ) * Space.S
        query_results = self.space.space.point_query(
            query_pos,
            max_distance=.5,
            shape_filter=pymunk.ShapeFilter(
                categories=Space.CAT_STATIC,
                mask=pymunk.ShapeFilter.ALL_MASKS(),
            )
        )
        constraints = []
        if not query_results:
            raise ValueError(f"String did not find something to attach at {self.init_positions[0]}")

        constraints.append(
            pymunk.PinJoint(
                query_results[0].shape.body, self.bodies[0],
                #(0.5, 0),
                query_results[0].shape.body.world_to_local(query_pos),
                (0, 0),
            )
        )
        for body, next_body in zip(self.bodies, self.bodies[1:]):
            con = pymunk.DampedSpring(
                body, next_body,
                (0, 0), (0, 0),
                rest_length=body.position.get_distance(next_body.position),
                stiffness=500.,
                damping=10.,
            )
            constraints.append(con)

        self.space.space.add(*self.bodies, *self.shapes, *constraints)

    def step(self, rs: RenderSettings):
        if self.sprite_render:
            self.sprite_render.locations = [
                body.position / self.space.S
                for body in self.bodies
            ]
            self.sprite_render.scales = [
                shape.radius / self.space.S
                for shape in self.shapes
            ]
            #print("BODY", self.bodies[0].position)
            #print(self.sprite_render.locations)

    def create_graph_objects(self):
        from ..graphics import MultiSpriteRender
        self.sprite_render = MultiSpriteRender(
            num_sprites=len(self.init_positions),
            #style=Style(texture_filename="texture/tileset2x2.png"),
        )
        yield self.sprite_render


