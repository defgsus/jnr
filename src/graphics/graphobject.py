import math
from typing import Optional, Union, Dict

import moderngl
import numpy as np
import pygame
import pyrr


from .rendersettings import RenderSettings
from .shadersource import preprocess_shader_source

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
            if isinstance(obj, GraphObject):
                obj._release()
            else:
                obj.release()
        self._gl_objects.clear()

    def _register_gl_objects(self):
        for name, obj in vars(self):
            if callable(getattr(obj, "release", None)):
                self._gl_objects[id(obj)] = obj


