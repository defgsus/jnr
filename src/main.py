import pygame
import moderngl
import pyrr
import numpy as np

from src.world import World


class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (1280, 720), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True
        )
        # pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()
        self.running = False
        self.start_tick = pygame.time.get_ticks() / 1000.
        self.dt = 0.
        self.world = World()

    def run(self):
        try:
            self.running = True
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    else:
                        self.handle_event(event)

                self.dt = self.clock.tick(60) / 1000
                self.second = pygame.time.get_ticks() / 1000.0 - self.start_tick
                rs = self.world.rendersettings(self.dt, self.second)
                self.world.step(rs)
                self.world.render(rs)
        finally:
            pygame.quit()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
