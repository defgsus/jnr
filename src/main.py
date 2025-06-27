import math
import random

import pygame
import moderngl
import pyrr.matrix44

from src.graphics.graphobject import SomeObject
from src.graphics import RenderSettings
from src.graphics.graphscene import GraphScene


class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (1280, 720), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True
        )
        pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()
        self.running = False
        self.start_tick = pygame.time.get_ticks() / 1000.
        self.dt = 0.
        self.gl = moderngl.get_context()
        self.graph_scene = GraphScene()

    def run(self):
        try:
            self.running = True
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        self.handle_event(event)

                self.dt = self.clock.tick(60) / 1000
                self.render()
        finally:
            pygame.quit()

    def handle_event(self, event: pygame.event.Event):
        pass

    def render(self):
        now = pygame.time.get_ticks() / 1000.0 - self.start_tick
        rs = RenderSettings(
            second=now,
            dt=self.dt,
            transformation=pyrr.matrix44.create_from_translation((math.sin(now), 0, 0)),
            projection=pyrr.matrix44.create_orthogonal_projection(-1, 1, -1, 1, -1, 1),
            gl=self.gl,
        )

        self.gl.clear(0, 0, 0)

        if not self.graph_scene.objects:
            self.graph_scene.add(SomeObject())

        self.graph_scene.render(rs)

        pygame.display.flip()

