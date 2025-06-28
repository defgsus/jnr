from .spaceobject import *
from .polygon import Polygon

import pygame


class Player(Polygon):

    def __init__(
            self,
            position: Tuple[float, float] = (0, 0),
    ):
        super().__init__(
            vertices=[(-1, -1), (1, -1), (1, 1), (-1, 1)],
            position=position,
            texture="texture/tileset2x2.png",
        )

    def step(self, rs: RenderSettings):
        keys = pygame.key.get_pressed()

        mapping = {
            pygame.K_UP: (0, 1),
            pygame.K_DOWN: (0, -1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
        }
        V = 5
        for key, impulse in mapping.items():
            if keys[key]:
                v = V
                if key == pygame.K_UP:
                    v *= 4
                self.body.apply_impulse_at_world_point(
                    (impulse[0]*v, impulse[1]*v),
                    self.body.position,
                )
        #if keys[pygame.K_DOWN]:
        #if keys[pygame.K_LEFT]:
        #if keys[pygame.K_RIGHT]:
        #print("P", self.position)