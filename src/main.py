import argparse
import tracemalloc

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
        self.world = World(self.screen)

    @classmethod
    def parse_args(cls) -> dict:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-tm", "--trace-malloc", type=bool, nargs="?", default=False, const=True,
        )
        return vars(parser.parse_args())

    def run(self, **kwargs):
        try:
            if kwargs["trace_malloc"]:
                tracemalloc.start(5)

            self._main_loop()

            if kwargs["trace_malloc"]:
                snapshot = tracemalloc.take_snapshot()
                print("--- trace-malloc ----")
                for i, stat in enumerate(snapshot.statistics("lineno")[:20]):
                    print(f"{i:2}: {stat}")
        finally:
            pygame.quit()

    def _main_loop(self):
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

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            #print(event)
            map_pos = self.world.screen_pos_to_map_pos(event.dict["pos"])
            s = self.world.physics.get_shapes_at(map_pos)
            print("S", s)
