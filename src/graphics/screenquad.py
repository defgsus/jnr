
from .graphobject import *
from .vertexarray import VertexArray
from src.assets import assets


class ScreenQuad(GraphObject):

    def __init__(
            self,
            texture_filename: str,
            z: float = 0.,
    ):
        super().__init__()
        self.vao: Optional[VertexArray] = None
        self.z = z
        self.texture_filename = texture_filename

    def initialize(self):
        self.vao = VertexArray(
            [
                -1, -1, 0,
                1, -1, 0,
                1, 1, 0.,

                -1, -1, 0,
                -1, 1, 0,
                1, 1, 0,
            ],
            """
            #version 330 core
            
            #include "default_uniforms.glsl"
            #line 32
            uniform float u_z;
            
            layout (location = 0) in vec3 in_vertex;
            
            out vec2 v_tex_coord;
            
            void main() {
                gl_Position = u_transformation * vec4(in_vertex, 1.0);
                gl_Position.z = u_z / 10000;
                //v_tex_coord = (u_world_transformation * vec4(in_vertex * .5 + .5, 1.0)).xy;
                v_tex_coord = in_vertex.xy * .5 + .5;
                v_tex_coord.xy -= (u_world_transformation * u_transformation)[3].xy / u_z;
            }
            """,
            """
            #version 330 core
            
            #include "default_uniforms.glsl"
            uniform float u_z;
            uniform sampler2D u_texture;

            in vec2 v_tex_coord;
            layout (location = 0) out vec4 out_color;
            
            void main() {
                vec2 t = v_tex_coord * u_z / 1000;
                out_color = texture(u_texture, t);
                //out_color = clamp(vec4(sin(t.x*7.), cos(t.y*5.), .5, sin(t.x*7.)), 0, 1);
            }
            """
        )
        image = assets.get_image(self.texture_filename)
        self.texture = self.gl.texture(image.size, 4, image.tobytes())
        self.sampler = self.gl.sampler(texture=self.texture)
        self.sampler.filter = (self.gl.LINEAR, self.gl.LINEAR)

    def render(self, rs: RenderSettings):
        self.sampler.use()
        self.vao.render(rs, uniforms={
            "u_z": self.z,
            "u_transformation": pyrr.matrix44.create_from_scale((4, 1, 1)).flatten().astype("f4"),
        })
