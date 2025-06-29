import pymunk

from .shapesettings import ShapeSettings
from .spaceobject import SpaceObject
from .space import Space
from src.maps.tiled import TiledMapLayer


class TileSpace(SpaceObject):

    def __init__(
            self,
            map: TiledMapLayer,
    ):
        super().__init__(
            shape_settings=ShapeSettings(
                friction=10.,
                static=True,
            ),
        )
        self.map = map

    def add_to_space(self):
        S = Space.S

        shapes = []
        grid = self.map.to_numpy()
        for y, row in enumerate(grid):
            wy = y * S
            for x, v in enumerate(row):
                wx = x * S
                if v:
                    shape = pymunk.Poly(
                        self.space.space.static_body,
                        [
                            (wx+0*S, wy+0*S),
                            (wx+1*S, wy+0*S),
                            (wx+1*S, wy+1*S),
                            (wx+0*S, wy+1*S),
                        ]
                    )
                    self.shape_settings.apply_to_shape(shape)

                    # print(shape.filter)
                    shapes.append(shape)

        self.space.space.add(*shapes)

