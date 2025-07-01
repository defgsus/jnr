from typing import List, Tuple

import pymunk

from src.graphics import RenderSettings, GraphScene
from .spaceobject import SpaceObject


class Space:

    # !! GLOBAL SCALE to make objects a bit more stable
    # don't forget when working directly with pymunk objects !!
    S = 10

    # pymunk.ShapeFilter categories
    CAT_STATIC = 0b00000001
    CAT_PLAYER = 0b00000010
    CAT_OBJECT = 0b00000100

    def __init__(self, world: "World"):
        from ..world import World
        self.space = pymunk.Space(threaded=True)
        self.space.gravity = 0, -300
        self.space.damping = 1
        self.space.iterations = 30
        self.objects: List[SpaceObject] = []
        self.world: World = world

    def step(self, rs: RenderSettings):
        for obj in self.objects:
            obj.step(rs)
        self.space.step(rs.dt)

    def add(self, obj: SpaceObject):
        obj.space = self
        try:
            obj.add_to_space()
        except Exception as e:
            e.args = (f"{e.args[0] if e.args else ''}\nFor object: {obj}", *e.args[1:])
            raise
        self.objects.append(obj)

    def create_graph_objects(self, scene: GraphScene):
        for space_obj in self.objects:
            for obj in space_obj.create_graph_objects():
                scene.add(obj)

    def get_shapes_at(self, pos: Tuple[int, int]):
        x, y = pos
        x *= self.S
        y *= self.S

        return self.space.point_query(
            (x, y),
            max_distance=0.,
            shape_filter=pymunk.ShapeFilter(
                categories=pymunk.ShapeFilter.ALL_CATEGORIES(),
                mask=pymunk.ShapeFilter.ALL_MASKS(),
            )
        )
