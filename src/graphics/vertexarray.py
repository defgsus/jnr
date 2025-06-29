import moderngl
import numpy as np
from typing import Union, Iterable, Optional, Dict

from .rendersettings import RenderSettings
from .shadersource import preprocess_shader_source


class VertexArray:

    gl: moderngl.Context
    progam: moderngl.Program
    vbo: moderngl.Buffer
    vao: moderngl.VertexArray

    def __init__(
            self,
            attributes: Dict[str, Union[Iterable[float], np.ndarray]],
            vertex_source: str,
            fragment_source: str,
    ):
        """
        :param attributes: something like:
            {
                "vertex": np.rand((100, 3)),
                "uv": np.rand((100, 2)),
            }
        """
        self.vertex_source = vertex_source
        self.fragment_source = fragment_source
        self.attributes: Dict[str, np.ndarray] = {}
        self.vbos: Dict[str, moderngl.Buffer] = {}
        self.vao: Optional[moderngl.VertexArray] = None
        self.program: Optional[moderngl.Program] = None
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
        attr_list = []
        for name, attr in self.attributes.items():
            self.vbos[name] = vbo = gl.buffer(attr.astype('f4').tobytes())
            attr_list.append((vbo, f"{attr.shape[-1]}f", f"in_{name}"))
        self.vao = self.gl.vertex_array(self.program, attr_list)

    def release(self):
        if self.vao is not None:
            self.vao.release()
            for vbo in self.vbos.values():
                vbo.release()
            self.program.release()
            self.vao = None
            self.program = None
            self.vbos.clear()

    def render(self, rs: RenderSettings, uniforms: Optional[dict] = None, instances: int = -1):
        if self.vao is None:
            self.initialize(rs.gl)

        rs.set_uniforms(self.program)
        if uniforms:
            for key, value in uniforms.items():
                self.program[key] = value
        self.vao.render(instances=instances)
