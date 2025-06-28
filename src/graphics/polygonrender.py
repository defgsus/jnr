from typing import List, Dict, Optional, Union, Tuple

from scipy.spatial import Delaunay

from .graphobject import *
from .vertexarray import VertexArray
from ..assets import assets
from ..physics.polygon import Polygon
from ..physics.circle import Circle


class PolygonRender(GraphObject):

    def __init__(
            self,
            polygon: Union[Polygon, Circle],
            texture: Optional[str] = None,
    ):
        super().__init__()
        self.polygon = polygon
        self.texture_filename = texture

    def initialize(self):
        vertices = self.triangulate()
        self.vao = VertexArray(
            vertices,
            attributes={
                **({"uv": self.get_uv_choords(vertices)} if self.texture_filename else {})
            },
            vertex_source="""
            #version 330 core
            
            #include "default_uniforms.glsl"

            layout (location = 0) in vec3 in_vertex;
            layout (location = 1) in vec2 in_uv;
            
            out vec2 v_uv;
            
            void main() {
                gl_Position = u_projection * u_world_transformation * u_transformation * vec4(in_vertex, 1.0);
                v_uv = in_uv;
            }
            """,
            fragment_source=f"""
            #version 330 core
            #line 47
            
            #define COLOR {1 if self.texture_filename else 0}
            
            uniform sampler2D u_texture;
            layout (location = 0) out vec4 out_color;
            in vec2 v_uv;
            
            void main() {{
            #if COLOR == 0
                out_color = vec4(.5, .5, .2, 1.);
            #elif COLOR == 1
                out_color = texture(u_texture, v_uv);
            #endif
            }}
            """
        )
        if self.texture_filename:
            image = assets.get_image(self.texture_filename)
            self.texture = self.gl.texture(image.size, 4, image.tobytes())
            self.sampler = self.gl.sampler(texture=self.texture)
            self.sampler.filter = (self.gl.LINEAR, self.gl.LINEAR)

    def render(self, rs: RenderSettings):
        pos = self.polygon.position

        trans = pyrr.matrix44.create_from_translation((*pos, 0))
        rot = pyrr.matrix44.create_from_z_rotation(-self.polygon.body.angle)
        trans = pyrr.matrix44.multiply(rot, trans)
        if self.texture_filename:
            self.sampler.use()
        self.vao.render(rs, uniforms={
            "u_transformation": trans.flatten().astype("f4"),
        })

    def triangulate(self):
        if isinstance(self.polygon, Circle):
            return self.triangulate_circle()

        triangles = Delaunay(
            self.polygon.vertices
        )

        vertices = []
        for tri in triangles.simplices:
            for idx in tri:
                vertices.extend(
                    triangles.points[idx]
                )
                vertices.append(0)

        return vertices

    def triangulate_circle(self, steps: int = 36):
        radius = self.polygon.radius

        vertices = []
        for step in range(steps):
            t0 = step / steps * math.pi * 2
            t1 = (step + 1) / steps * math.pi * 2
            x0 = math.sin(t0) * radius
            y0 = math.cos(t0) * radius
            x1 = math.sin(t1) * radius
            y1 = math.cos(t1) * radius

            vertices.extend([
                0, 0, 0,
                x0, y0, 0,
                x1, y1, 0,
            ])
        return vertices

    def get_uv_choords(self, vertices: List[float]):
        min_x, max_x = min(vertices[::3]), max(vertices[::3])
        min_y, max_y = min(vertices[1::3]), max(vertices[1::3])
        uvs = []
        for x, y in zip(vertices[::3], vertices[1::3]):
            u = (x - min_x) / (max_x - min_x)
            v = (y - min_y) / (max_y - min_y)
            uvs.append([u, v])
        return uvs
