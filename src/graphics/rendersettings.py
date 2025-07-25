import dataclasses

import moderngl
import pyrr


@dataclasses.dataclass
class RenderSettings:
    second: float
    dt: float
    transformation: pyrr.Matrix44
    projection: pyrr.Matrix44
    gl: moderngl.Context

    def set_uniforms(self, shader: moderngl.Program):
        if "u_time" in shader:
            shader["u_time"].write(self.second)
        if "u_dt" in shader:
            shader["u_dt"].write(self.dt)
        if "u_world_transformation" in shader:
            shader["u_world_transformation"].write(self.transformation.flatten().astype("f4"))
        if "u_projection" in shader:
            shader["u_projection"].write(self.projection.flatten().astype("f4"))

    def init_gl_state(self):
        self.gl.disable(self.gl.DEPTH_TEST)
        self.gl.enable(self.gl.BLEND)
        #self.gl.(self.gl.ONE_MINUS_SRC_ALPHA)
