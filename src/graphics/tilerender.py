from typing import Tuple

from .graphobject import *
from .vertexarray import VertexArray
from ..assets import assets
from src.maps.tiledmap import TiledMapLayer


class TileRender(GraphObject):

    def __init__(
            self,
            map: TiledMapLayer,
            texture: str,
            num_tiles: Tuple[int, int],
            mapping: Optional[Dict[int, Tuple[int, int]]] = None,
    ):
        super().__init__()
        self.map = map
        self.vertices = []
        self.uv_coords = []
        self.texture_filename = texture
        if not mapping:
            mapping = {}
            for y in range(num_tiles[1]):
                for x in range(num_tiles[0]):
                    mapping[len(mapping) + 1] = x, num_tiles[1] - 1 - y

        grid = self.map.to_numpy()
        for y, row in enumerate(grid):
            for x, v in enumerate(row):
                if v:
                    self.vertices.extend([
                        x, y, 0,
                        x+1, y, 0,
                        x+1, y+1, 0.,

                        x, y, 0,
                        x, y+1, 0,
                        x+1, y+1, 0,
                    ])
                    tile_x, tile_y = mapping[v]
                    tx0 = tile_x / num_tiles[0]
                    tx1 = (tile_x + 1) / num_tiles[0]
                    ty0 = tile_y / num_tiles[0]
                    ty1 = (tile_y + 1) / num_tiles[0]
                    self.uv_coords.extend([
                        [tx0, ty0],
                        [tx1, ty0],
                        [tx1, ty1],

                        [tx0, ty0],
                        [tx0, ty1],
                        [tx1, ty1],
                    ])
        self.vertices = np.array(self.vertices).reshape(-1, 3)

    def initialize(self):
        self.vao = VertexArray(
            attributes={
                "vertex": self.vertices,
                "uv": self.uv_coords,
            },
            vertex_source="""
            #version 330 core
            
            #include "default_uniforms.glsl"

            in vec3 in_vertex;
            in vec2 in_uv;
            
            out vec2 v_uv;
            
            void main() {
                gl_Position = u_projection * u_world_transformation * vec4(in_vertex, 1.0);
                v_uv = in_uv;
            }
            """,
            fragment_source="""
            #version 330 core
            
            uniform sampler2D u_texture;
            layout (location = 0) out vec4 out_color;
            in vec2 v_uv;
            
            void main() {
                out_color = texture(u_texture, v_uv);//vec4(v_uv.x, v_uv.y, 1.0, 1.0);
            }
            """
        )
        image = assets.get_image(self.texture_filename)
        self.texture = self.gl.texture(image.size, 4, image.tobytes())
        self.sampler = self.gl.sampler(texture=self.texture)
        self.sampler.filter = (self.gl.NEAREST, self.gl.NEAREST)

    def render(self, rs: RenderSettings):
        self.sampler.use()
        self.vao.render(rs)
