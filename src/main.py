import pygame
import moderngl
import pyrr
import numpy as np

from src.graphics import *
from src.graphics.screenquad import ScreenQuad
from src import physics
from src.assets import assets


class SomeObject(GraphObject):

    def initialize(self):
        self.vao = VertexArray(
            [
                0.0, 0.4, 0.0,
                -0.4, -0.3, 0.0,
                0.4, -0.3, 0.0,
            ],
            """
            #version 330 core
            
            #include "default_uniforms.glsl"

            layout (location = 0) in vec3 in_vertex;
            
            //out vec3 v_position;
            
            void main() {
                gl_Position = u_projection * u_world_transformation * vec4(in_vertex, 1.0);
            }
            """,
            """
            #version 330 core

            layout (location = 0) out vec4 out_color;

            void main() {
                out_color = vec4(1.0, 1.0, 1.0, 1.0);
            }
            """
        )

    def render(self, rs: RenderSettings):
        self.vao.render(rs)



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
        self.gl = moderngl.get_context()
        self.graph_scene = GraphScene()
        self.velocity = pyrr.Vector3()
        self.translation = pyrr.Vector3()
        self.scale = 1.
        self.physics = physics.Space()
        self.demo_map = assets.get_tiled_map("maps/map128x128.json")
        self.physics.add(physics.TileSpace(self.demo_map.layer(0)))
        self.player = physics.Player(position=(10, 10))
        self.physics.add(self.player)
        for i in range(50):
            self.physics.add(physics.Circle(radius=.5, position=(5+i%10, 20+i//10)))
        self.physics.add(physics.Polygon(
            vertices=[(-1000, -10), (1000, -10), (1000, 0), (0, 0)],
            static=True,
        ))

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
                self.step()
                self.render()
        finally:
            pygame.quit()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()

    def rendersettings(self):
        scale = self.scale * 2
        w, h = pygame.display.get_window_size()
        x_scale = w / h
        return RenderSettings(
            second=self.second,
            dt=self.dt,
            transformation=
                #self.translation,#pyrr.matrix44.create_from_translation((math.sin(self.second), math.sin(self.second/5.168), 0)),
                pyrr.matrix44.inverse(
                    pyrr.matrix44.create_from_translation(self.translation)
                ),
            projection=
                pyrr.matrix44.create_orthogonal_projection(-scale*x_scale, scale*x_scale, -scale, scale, 1, -1000),
            gl=self.gl,
        )

    def step(self):
        rs = self.rendersettings()
        keys = pygame.key.get_pressed()

        v = self.dt * 10
        #if keys[pygame.K_UP]:
            #self.player.body.kinetic_energy =
            #self.velocity += pyrr.Vector3([0, 1, 0]) * v
        #if keys[pygame.K_DOWN]:
        #    self.velocity += pyrr.Vector3([0, -1, 0]) * v
        #if keys[pygame.K_LEFT]:
        #    self.velocity += pyrr.Vector3([-1, 0, 0]) * v
        #if keys[pygame.K_RIGHT]:
        #    self.velocity += pyrr.Vector3([1, 0, 0]) * v

        difference = (pyrr.Vector3([*self.player.position, 0]) - self.translation)
        self.velocity += v * difference
        self.scale += v * np.sum(np.abs(difference)).item()
        self.translation += self.velocity * v
        #print(self.translation)
        self.translation[2] = 0
        self.velocity *= 1. - v*3
        self.scale += v * (4. - self.scale)
        self.physics.step(rs)

    def render(self):
        rs = self.rendersettings()

        self.gl.clear(0, 0, 0)

        if not self.graph_scene.objects:
            self.graph_scene.add(ScreenQuad(z=3000, texture_filename="texture/background/sky3x1.png"))
            self.graph_scene.add(ScreenQuad(z=2000, texture_filename="texture/background/clouds3x1.png"))
            self.graph_scene.add(ScreenQuad(z=1000, texture_filename="texture/background/mountains4x1.png"))
            self.graph_scene.add(SomeObject())
            self.graph_scene.add(TileRender(
                map=self.demo_map.layer(0),
                texture="texture/tileset2x2.png",
                num_tiles=(2, 2),
            ))
            self.physics.create_graph_objects(self.graph_scene)

        self.graph_scene.render(rs)
        #pymunk.pygame_util.positive_y_is_up = True
        #self.physics.space.debug_draw(pymunk.pygame_util.DrawOptions(self.screen))

        pygame.display.flip()

