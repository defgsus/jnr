import math
from typing import Optional, Union, Dict

import moderngl
import numpy as np
import pygame
import pyrr


from .rendersettings import RenderSettings

GLObject = Union[moderngl.VertexArray, moderngl.Buffer, moderngl.Framebuffer]

class GraphObject:

    def __init__(
            self,
    ):
        self.gl: Optional[moderngl.Context] = None
        self._gl_objects: Dict[int, GLObject] = {}

    def initialize(self):
        pass

    def release(self):
        pass

    def render(self, rs: RenderSettings):
        raise NotImplementedError

    def _initialize(self, gl: moderngl.Context):
        self.gl = gl
        self.initialize()

    def _release(self):
        for obj in self._gl_objects.values():
            if hasattr(obj, "release"):
                obj.release()
        self._gl_objects.clear()

    def _register_gl_objects(self):
        for name, obj in vars(self):
            if isinstance(obj, GLObject):
                self._gl_objects[id(obj)] = obj


class SomeObject(GraphObject):

    def initialize(self):
        self.program = self.gl.program(
            vertex_shader='''
                #version 330 core
                
                uniform float u_time;
                uniform float u_dt;
                uniform mat4 u_transformation;
                uniform mat4 u_projection;

                layout (location = 0) in vec3 in_vertex;
                
                //out vec3 v_position;
                
                void main() {
                    gl_Position = u_projection * u_transformation * vec4(in_vertex, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330 core

                layout (location = 0) out vec4 out_color;

                void main() {
                    out_color = vec4(1.0, 1.0, 1.0, 1.0);
                }
            ''',
        )

        vertices = np.array([
            0.0, 0.4, 0.0,
            -0.4, -0.3, 0.0,
            0.4, -0.3, 0.0,
        ])

        self.vbo = self.gl.buffer(vertices.astype('f4').tobytes())
        self.vao = self.gl.vertex_array(self.program, [(self.vbo, '3f', 'in_vertex')])

    def render(self, rs: RenderSettings):
        self.gl.enable(self.gl.DEPTH_TEST)
        rs.set_uniforms(self.program)
        self.vao.render()
