import math
import random
from typing import Tuple, Optional, List, Iterable
import pymunk

from .shapesettings import ShapeSettings
from .spaceobject import SpaceObject
from .space import Space
from src.maps.tiledmap import TiledMapLayer
from ..graphics import Style, MultiSpriteRender, RenderSettings
from ..graphics.polygonrender import PolygonRender


class Enemy(SpaceObject):

    def __init__(
            self,
            position: Tuple[float, float] = (0, 0),
            shape_settings: Optional[ShapeSettings] = None,
            style: Optional[Style] = None,
            name: Optional[str] = None,
            radius1: float = .5,
            radius2: float = .7,
            radius3: float = .15,
            num_feet: int = 5,
    ):
        super().__init__(
            shape_settings=shape_settings or ShapeSettings(
                friction=10.,
                mass=.1,
            ),
            style=style or Style(
                texture_filename="texture/evil-sphere.png",
            ),
            name=name or "enemy",
        )
        self.initial_position = position
        self.feet_render: MultiSpriteRender = None
        self.feet: List[pymunk.Body] = []
        self.feet_joints: List[Tuple[pymunk.SlideJoint, float]] = []
        self.radius1 = radius1
        self.radius2 = radius2
        self.radius3 = radius3
        self.num_feet = num_feet

    @property
    def position(self) -> pymunk.Vec2d:
        return self.body.position / Space.S

    def add_to_space(self):
        S = Space.S
        world_init_position = pymunk.Vec2d(*self.initial_position)

        objects = []
        self.body = pymunk.Body()
        self.body.position = world_init_position * S
        self.shape = pymunk.Circle(self.body, self.radius1 * S)
        self.shape_settings.apply_to_shape(self.shape)
        objects.append(self.body)
        objects.append(self.shape)

        for i in range(self.num_feet):
            positions = [
                pymunk.Vec2d(0, 1).rotated((i + o) / self.num_feet * math.pi * 2)
                for o in (0., .5, 1.)
            ]
            world_foot_pos = world_init_position + positions[1] * self.radius2
            body = pymunk.Body()
            body.position = world_foot_pos * S
            shape = pymunk.Circle(body, self.radius3 * S)
            self.shape_settings.apply_to_shape(shape)
            objects.append(body)
            objects.append(shape)
            self.feet.append(body)

            for pos in (positions[0], positions[1]):
                world_attach_pos = world_init_position + pos * self.radius1 * .9
                rest_length = world_foot_pos.get_distance(world_attach_pos) * S
                joint = pymunk.SlideJoint(
                    body, self.body,
                    body.world_to_local(world_foot_pos * S), self.body.world_to_local(world_attach_pos * S),
                    min=rest_length,
                    max=rest_length,
                )
                objects.append(joint)
                self.feet_joints.append((joint, rest_length))

        self.space.space.add(*objects)

    def create_graph_objects(self) -> Iterable["GraphObject"]:
        yield PolygonRender(self, style=self.style)
        self.feet_render = MultiSpriteRender(self.num_feet, style=self.style)
        yield self.feet_render

    def step(self, rs: RenderSettings):
        self.feet_render.locations = [
            body.position / Space.S
            for body in self.feet
        ]
        self.feet_render.scales = self.radius3

        #if random.uniform(0, 1) < rs.dt:
        #    imp = (0, 1.)
        #    self.body.apply_impulse_at_local_point(imp, (0, 0))

        direction = 1 if self.space.world.player.position.x > self.position.x else -1
        active_feet = int(rs.second * 4 * direction) % self.num_feet
        for i, (joint, rest_length) in enumerate(self.feet_joints):
            new_len = rest_length
            if i // 2 == active_feet:
                new_len = rest_length * 2
            joint.min = joint.max = new_len
