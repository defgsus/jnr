from typing import List

import pymunk

from src.graphics import RenderSettings, GraphScene
from .spaceobject import SpaceObject


class Space:

    S = 10

    def __init__(self):
        self.space = pymunk.Space(threaded=True)
        self.space.gravity = 0, -90
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

