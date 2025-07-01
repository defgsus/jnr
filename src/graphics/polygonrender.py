from typing import List, Dict, Optional, Union, Tuple

import numpy as np
from scipy.spatial import Delaunay

from .style import Style
from .graphobject import *
from .vertexarray import VertexArray
from ..assets import assets
from ..physics.polygon import Polygon
from ..physics.circle import Circle


class PolygonRender(GraphObject):

    def __init__(
            self,
            polygon: Union[Polygon, Circle],
            style: Optional[Style] = None,
    ):
        super().__init__()
        self.polygon = polygon
        self.style = style or Style()

    def initialize(self):
        vertices = self.triangulate()
        self.vao = VertexArray(
            attributes={
                "vertex": vertices,
                **({"uv": self.get_uv_choords(vertices)} if self.style.has_texture else {})
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
        if self.style.has_texture:
            self.sampler = self.style.to_texture_sampler(self.gl)

    def render(self, rs: RenderSettings):
        pos = self.polygon.position

        trans = pyrr.matrix44.create_from_translation((*pos, 0))
        if self.style.show_rotation:
            trans = pyrr.matrix44.multiply(
                pyrr.matrix44.create_from_z_rotation(-self.polygon.body.angle),
                trans
            )
        trans = pyrr.matrix44.multiply(
            pyrr.matrix44.create_from_scale((*self.style.scale, 0)),
            trans,
        )

        uniforms = {
            "u_transformation": trans.flatten().astype("f4"),
        }
        if self.style.has_texture:
            self.sampler.use()

            if self.style.tileset:
                uniforms.update(self.style.tileset_controller.uniforms())

        self.vao.render(rs, uniforms=uniforms)

    def triangulate(self):
        if not isinstance(self.polygon, Polygon):
            return self.triangulate_circle()

        triangles = Delaunay(
            self.polygon.vertices
        )

        vertices = []
        for tri in triangles.simplices:
            for idx in tri:
                vertices.append([*triangles.points[idx], 0])

        return np.array(vertices)

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
                [0, 0, 0],
                [x0, y0, 0],
                [x1, y1, 0],
            ])
        return np.array(vertices)

    def get_uv_choords(self, vertices: np.ndarray):
        min_x, max_x = vertices[:, 0].min(), vertices[:, 0].max()
        min_y, max_y = vertices[:, 1].min(), vertices[:, 1].max()
        uvs = vertices[:, :2].copy()
        uvs[:, 0] = (uvs[:, 0] - min_x) / (max_x - min_x)
        uvs[:, 1] = (uvs[:, 1] - min_y) / (max_y - min_y)
        return uvs
