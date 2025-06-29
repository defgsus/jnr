import random

import pygame
import moderngl
import pyrr
import numpy as np

from src import physics, graphics
from src.assets import assets
from src.graphics import Style


class World:

    def __init__(self):
        self.physics = physics.Space()
        self.graph_scene = graphics.GraphScene()
        self.gl = moderngl.get_context()

        self.velocity = pyrr.Vector3()
        self.translation = pyrr.Vector3()
        self.scale = 1.
        self.target_scale = 2.

        self.demo_map = assets.get_tiled_map("maps/map128x128.json")
        self.physics.add(physics.TileSpace(self.demo_map.layer(0)))

        self.player = physics.Player(position=(22, 10))

        self.physics.add(self.player)
        for i in range(100):
            self.physics.add(physics.Circle(
                radius=random.uniform(0.1, .7),
                position=(4+i%4, 20+i//4))
            )
        self.physics.add(physics.Polygon(
            vertices=[(-1000, -10), (1000, -10), (1000, 0), (-1000, -10)],
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
        self.demo_sprites = graphics.MultiSpriteRender(
            num_sprites=20,
            style=Style(texture_filename="texture/tileset2x2.png"),
        )
        self.graph_scene.add(self.demo_sprites)
        self.physics.create_graph_objects(self.graph_scene)

    def step(self, rs: graphics.RenderSettings):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_PLUS]:
            self.target_scale *= 1 - rs.dt
        elif keys[pygame.K_MINUS]:
            self.target_scale *= 1 + rs.dt

        v = rs.dt * 10

        difference = (pyrr.Vector3([*self.player.position, 0]) - self.translation)
        self.velocity += v * difference
        self.scale += v * np.sum(np.abs(difference)).item()
        self.translation += self.velocity * v
        #print(self.translation)
        self.translation[2] = 0
        self.velocity *= 1. - v*3
        self.scale += v * (self.target_scale - self.scale)
        self.physics.step(rs)

        t = np.linspace(0, 2*np.pi, self.demo_sprites.num_sprites)
        self.demo_sprites.locations[:, 0] = np.sin(t+rs.second) * 10
        self.demo_sprites.locations[:, 1] = np.cos(t+rs.second*.618) * 10
        self.demo_sprites.rotations = np.sin(t+rs.second)

        #self.demo_sprites.locations = np.random.rand(self.demo_sprites.num_sprites, 2) * 20

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

