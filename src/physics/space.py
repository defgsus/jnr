from typing import List, Tuple

import pymunk

from src.graphics import RenderSettings, GraphScene
from .spaceobject import SpaceObject


class Space:

    # !! GLOBAL SCALE to make objects a bit more stable
    # don't forget when working directly with pymunk objects !!
    S = 10

    def __init__(self):
        self.space = pymunk.Space(threaded=True)
        self.space.gravity = 0, -140
        self.objects: List[SpaceObject] = []

    def step(self, rs: RenderSettings):
        for obj in self.objects:
            obj.step(rs)
        self.space.step(rs.dt)

    def add(self, obj: SpaceObject):
        obj.add_to_space(self.space)
        self.objects.append(obj)

    def create_graph_objects(self, scene: GraphScene):
        for space_obj in self.objects:
            obj = space_obj.create_graph_object()
            if obj:
                scene.add(obj)

    def get_shape_at(self, pos: Tuple[int, int], r: float = 0.01):
        x, y = pos
        x *= self.S
        y *= self.S
        bb = pymunk.BB(left=x-r, top=y-r, right=x+r, bottom=y+r)
        self.space.bb_query(bb)
