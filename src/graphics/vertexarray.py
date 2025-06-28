import moderngl
import numpy as np
from typing import Union, Iterable, Optional, Dict

from . import RenderSettings
from .shadersource import preprocess_shader_source


class VertexArray:

    gl: moderngl.Context
    progam: moderngl.Program
    vbo: moderngl.Buffer
    vao: moderngl.VertexArray

    def __init__(
            self,
            vertices: Union[Iterable[float], np.ndarray],
            vertex_source: str,
            fragment_source: str,
            attributes: Union[None, Dict[str, Union[Iterable[float], np.ndarray]]] = None,
    ):
        if not isinstance(vertices, np.ndarray):
            vertices = np.array(vertices)
        self.vertices = vertices
        self.vertex_source = vertex_source
        self.fragment_source = fragment_source
        self.vbo: Optional[moderngl.Buffer] = None
        self.attributes: Dict[str, np.ndarray] = {}
        self.attribute_vbos: Dict[str, moderngl.Buffer] = {}
        self.vao: Optional[moderngl.VertexArray] = None
        if attributes:
            for name, attr in attributes.items():
                if attr is None:
                    raise ValueError(f"'None' attribute name='{name}'")
                if not isinstance(attr, np.ndarray):
                    attr = np.array(attr)
                self.attributes[name] = attr

    def initialize(self, gl: moderngl.Context):
        self.gl = gl
        self.program = self.gl.program(
            vertex_shader=preprocess_shader_source(self.vertex_source),
            fragment_shader=preprocess_shader_source(self.fragment_source),
        )
        self.vbo = self.gl.buffer(self.vertices.astype('f4').tobytes())
        attr_list = [(self.vbo, '3f', 'in_vertex')]
        for name, attr in self.attributes.items():
            self.attribute_vbos[name] = vbo = gl.buffer(attr.astype('f4').tobytes())
            attr_list.append((vbo, f"{attr.shape[-1]}f", f"in_{name}"))
        self.vao = self.gl.vertex_array(self.program, attr_list)

    def release(self):
        if self.vao is not None:
            self.vao.release()
            self.vbo.release()
            self.program.release()
            self.vao = None
            self.vbo = None
            self.program = None

    def render(self, rs: RenderSettings, uniforms: Optional[dict] = None):
        if self.vao is None:
            self.initialize(rs.gl)

        rs.set_uniforms(self.program)
        if uniforms:
            for key, value in uniforms.items():
                self.program[key] = value
        self.vao.render()
