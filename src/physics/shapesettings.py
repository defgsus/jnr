import dataclasses
from typing import Optional

import pymunk


@dataclasses.dataclass
class ShapeSettings:
    mass: float = 1.
    density: float = 1.
    friction: float = 1.
    elasticity: float = 0.
    static: bool = False
    kinematic: bool = False
    filter: Optional[pymunk.ShapeFilter] = None

    def __post_init__(self):
        if self.static and self.kinematic:
            raise ValueError("Can only set static OR kinematic to True, not both")
        from .space import Space
        if self.filter is None:
            if self.static:
                self.filter = pymunk.ShapeFilter(
                    categories=Space.CAT_STATIC,
                    mask=pymunk.ShapeFilter.ALL_MASKS(),
                )
            else:
                self.filter = pymunk.ShapeFilter(
                    categories=pymunk.ShapeFilter.ALL_CATEGORIES(),
                    mask=pymunk.ShapeFilter.ALL_MASKS(),
                )

    @property
    def body_type(self):
        if self.static:
            return pymunk.Body.STATIC
        if self.kinematic:
            return pymunk.Body.KINEMATIC
        return pymunk.Body.DYNAMIC

    def apply_to_shape(self, shape: pymunk.Shape):
        shape.friction = self.friction
        shape.density = self.density
        shape.elasticity = self.elasticity
        shape.mass = self.mass
        shape.filter = self.filter
