from typing import List, Dict, Optional, Union, Tuple

import numpy as np

from .style import Style
from .graphobject import *
from .vertexarray import VertexArray
from ..assets import assets


class MultiSpriteRender(GraphObject):

    def __init__(
            self,
            num_sprites: int,
            style: Optional[Style] = None,
    ):
        super().__init__()
        self.num_sprites = num_sprites
        self.style = style or Style()
        # x, y, scale, rotation
        self._sprite_data = np.zeros((self.num_sprites, 4))
        self._sprite_data[:, 2] = 1

    @property
    def locations(self) -> np.ndarray:
        return self._sprite_data[:, :2]

    @locations.setter
    def locations(self, locations: np.ndarray):
        self._sprite_data[:, :2] = locations

    @property
    def scales(self) -> np.ndarray:
        return self._sprite_data[:, 2]

    @scales.setter
    def scales(self, scales: np.ndarray):
        self._sprite_data[:, 2] = scales

    @property
    def rotations(self) -> np.ndarray:
        return self._sprite_data[:, 3]

    @rotations.setter
    def rotations(self, rotations: np.ndarray):
        self._sprite_data[:, 3] = rotations

    def initialize(self):
        self.vao = VertexArray(
            attributes={
                "vertex": np.array([
                    -1, -1, 0,
                    1, -1, 0,
                    1, 1, 0.,

                    -1, -1, 0,
                    -1, 1, 0,
                    1, 1, 0,
                ]).reshape(-1, 3),
                **(
                    {"uv": np.array([
                        0, 0,
                        1, 0,
                        1, 1,

                        0, 0,
                        0, 1,
                        1, 1
                    ]).reshape(-1, 2),
                    }
                    if self.style.has_texture else {}
                ),
            },
            vertex_source="""
            #version 330 core
            
            #include "default_uniforms.glsl"
            #include "trigo.glsl"
            #line 75
            
            in vec3 in_vertex;
            in vec2 in_uv;
            layout (location = 3) in vec4 in_sprite;
            
            out vec2 v_uv;
            
            void main() {
                vec4 pos = vec4(in_vertex, 1.0);
                pos.xy = rotate_z(pos.xy, in_sprite.w) * in_sprite.z + in_sprite.xy;
                gl_Position = u_projection * u_world_transformation * pos;
                v_uv = in_uv;
            }
            """,
            fragment_source=f"""
            #version 330 core
            #line 97
            
            #define COLOR {(2 if self.style.tileset else 1) if self.style.has_texture else 0}
            
            uniform sampler2D u_texture;
            uniform vec4 u_uv_scale_offset;
            in vec2 v_uv;
            layout (location = 0) out vec4 out_color;
            
            void main() {{
            #if COLOR == 0
                out_color = vec4(.8, 1., .8, 1.);
            #elif COLOR == 1
                out_color = texture(u_texture, v_uv);
            #elif COLOR == 2
                vec2 uv = v_uv * u_uv_scale_offset.xy + u_uv_scale_offset.zw;
                out_color = texture(u_texture, uv);
            #endif
            }}
            """
        )
        self.sprite_vbo = self.gl.buffer(
            self._sprite_data.astype('f4').tobytes(),
            dynamic=True,
        )
        self.sprite_vbo.assign(3)

        if self.style.has_texture:
            self.sampler = self.style.to_texture_sampler(self.gl)

    def render(self, rs: RenderSettings):
        uniforms = {}
        if self.style.has_texture:
            self.sampler.use()

            if self.style.tileset:
                uniforms.update(self.style.tileset_controller.uniforms())

        self.sprite_vbo.write(self._sprite_data.astype("f4").tobytes())
        if self.vao.gl is None:
            self.vao.initialize(self.gl)
        self.vao.vao.bind(
            attribute=3, cls="f", buffer=self.sprite_vbo,
            fmt="4f",
            divisor=1,
        )
        self.vao.render(rs, uniforms=uniforms, instances=self.num_sprites)
