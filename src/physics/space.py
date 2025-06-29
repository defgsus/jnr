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

    def __init__(self):
        self.space = pymunk.Space(threaded=True)
        self.space.gravity = 0, -140
        self.objects: List[SpaceObject] = []

    def step(self, rs: RenderSettings):
        for obj in self.objects:
            obj.step(rs)
        self.space.step(rs.dt)

    def add(self, obj: SpaceObject):
        obj.space = self
        obj.add_to_space()
        self.objects.append(obj)

    def create_graph_objects(self, scene: GraphScene):
        for space_obj in self.objects:
            obj = space_obj.create_graph_object()
            if obj:
                scene.add(obj)

    def get_shapes_at(self, pos: Tuple[int, int]):
        x, y = pos
        x *= self.S
        y *= self.S
        print("QUERY", (x, y))
        return self.space.point_query(
            (x, y),
            max_distance=0.,
            shape_filter=pymunk.ShapeFilter(
                categories=pymunk.ShapeFilter.ALL_CATEGORIES(),
                mask=pymunk.ShapeFilter.ALL_MASKS(),
            )
        )
