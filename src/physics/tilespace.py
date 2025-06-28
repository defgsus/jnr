import pymunk

from .spaceobject import SpaceObject
from .space import Space
from src.maps.tiled import TiledMapLayer


class TileSpace(SpaceObject):

    def __init__(
            self,
            map: TiledMapLayer,
    ):
        super().__init__()
        self.map = map

    def add_to_space(self, space: pymunk.Space):
        self.space = space
        S = Space.S

        grid = self.map.to_numpy()
        for y, row in enumerate(grid):
            wy = y * S
            for x, v in enumerate(row):
                wx = x * S
                if v:
                    shape = pymunk.Poly(
                        self.space.static_body,
                        [
                            (wx+0*S, wy+0*S),
                            (wx+1*S, wy+0*S),
                            (wx+1*S, wy+1*S),
                            (wx+0*S, wy+1*S),
                        ]
                    )
                    self.space.add(shape)

