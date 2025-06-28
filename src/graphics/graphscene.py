from typing import List, Dict, Optional, Union

import moderngl

from .rendersettings import RenderSettings
from .graphobject import GraphObject


class GraphScene:

    def __init__(self):
        self.objects: List[GraphObject] = []
        self.is_initialized: Dict[GraphObject, bool] = {}

    def initialize(self, gl: moderngl.Context):
        for obj in self.objects:
            obj._initialize(gl)

    def release(self):
        for obj in self.objects:
            if obj in self.is_initialized:
                obj.release()
                self.is_initialized.pop(obj)

    def render(self, rs: RenderSettings):
        rs.init_gl_state()
        for obj in self.objects:
            if obj not in self.is_initialized:
                obj._initialize(rs.gl)
                self.is_initialized[obj] = True
            obj.render(rs)

    def add(self, obj: GraphObject):
        self.objects.append(obj)
