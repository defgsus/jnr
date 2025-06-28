import random

import pygame
import moderngl
import pyrr
import numpy as np

from src import physics, graphics
from src.assets import assets


class World:

    def __init__(self):
        self.physics = physics.Space()
        self.graph_scene = graphics.GraphScene()
        self.gl = moderngl.get_context()

        self.velocity = pyrr.Vector3()
        self.translation = pyrr.Vector3()
        self.scale = 1.

        self.demo_map = assets.get_tiled_map("maps/map128x128.json")
        self.physics.add(physics.TileSpace(self.demo_map.layer(0)))
        self.player = physics.Player(position=(10, 10))
        self.physics.add(self.player)
        for i in range(50):
            self.physics.add(physics.Circle(radius=random.uniform(0.1, .7), position=(5+i%10, 20+i//10)))
        self.physics.add(physics.Polygon(
            vertices=[(-1000, -10), (1000, -10), (1000, 0), (0, 0)],
            static=True,
        ))

        self.graph_scene.add(
            graphics.ScreenQuad(z=3000, texture_filename="texture/background/sky3x1.png")
        )
        self.graph_scene.add(
            graphics.ScreenQuad(z=2000, texture_filename="texture/background/clouds3x1.png")
        )
        self.graph_scene.add(
            graphics.ScreenQuad(z=1000, texture_filename="texture/background/mountains4x1.png")
        )
        self.graph_scene.add(graphics.TileRender(
            map=self.demo_map.layer(0),
            texture="texture/tileset2x2.png",
            num_tiles=(2, 2),
        ))
        self.physics.create_graph_objects(self.graph_scene)

    def step(self, rs: graphics.RenderSettings):
        keys = pygame.key.get_pressed()

        v = rs.dt * 10

        difference = (pyrr.Vector3([*self.player.position, 0]) - self.translation)
        self.velocity += v * difference
        self.scale += v * np.sum(np.abs(difference)).item()
        self.translation += self.velocity * v
        #print(self.translation)
        self.translation[2] = 0
        self.velocity *= 1. - v*3
        self.scale += v * (2. - self.scale)
        self.physics.step(rs)

    def render(self, rs: graphics.RenderSettings):
        self.gl.clear(0, 0, 0)

        self.graph_scene.render(rs)
        #pymunk.pygame_util.positive_y_is_up = True
        #self.physics.space.debug_draw(pymunk.pygame_util.DrawOptions(self.screen))

        pygame.display.flip()

    def rendersettings(self, dt: float, second: float):
        scale = self.scale * 2
        w, h = pygame.display.get_window_size()
        x_scale = w / h
        return graphics.RenderSettings(
            second=second,
            dt=dt,
            transformation=
                #self.translation,#pyrr.matrix44.create_from_translation((math.sin(self.second), math.sin(self.second/5.168), 0)),
                pyrr.matrix44.inverse(
                    pyrr.matrix44.create_from_translation(self.translation)
                ),
            projection=
            pyrr.matrix44.create_orthogonal_projection(-scale*x_scale, scale*x_scale, -scale, scale, 1, -1000),
            gl=self.gl,
        )
