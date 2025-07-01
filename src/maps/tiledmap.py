import json
from pathlib import Path
from typing import Union, Tuple, List, Optional

import numpy as np
from pygame.draw import polygon


class TiledMapObject:

    def __init__(self, layer: "TiledMapLayer", data: dict):
        self.layer = layer
        self.map = layer.map
        self.id = data["id"]
        self.name = data["name"]
        self.pixel_width = data["width"]
        self.pixel_height = data["height"]
        self.pixel_x = data["x"]
        self.pixel_y = data["y"]
        self.type = data["type"]
        self.x = self.pixel_x / self.map.tile_width
        self.y = self.pixel_y / self.map.tile_height
        if "-up" in self.map.render_order:
            self.y = self.map.height - self.y
        self.pos = (self.x, self.y)
        self.width = self.pixel_width / self.map.tile_width
        self.height = self.pixel_height / self.map.tile_height
        self.properties = {
            p["name"]: p["value"]
            for p in (data.get("properties") or [])
        }
        self.world_polygon = []
        for p in (data.get("polygon") or []):
            x, y = p["x"] / self.map.tile_width, p["y"] / self.map.tile_height
            if "-up" in self.map.render_order:
                y = -y
            self.world_polygon.append((self.x + x, self.y + y))


class TiledMapLayer:

    def __init__(self, map: "TiledMap", index: int):
        self.map = map
        self.index = index
        self._objects: List[TiledMapObject] = None

    @property
    def data(self):
        return self.map.data["layers"][self.index]

    @property
    def width(self) -> int:
        return self.data["width"]

    @property
    def height(self) -> int:
        return self.data["height"]

    @property
    def size(self) -> Tuple[int, int]:
        return self.data["width"], self.data["height"]

    @property
    def render_order(self) -> str:
        return self.map.render_order

    def to_numpy(self) -> np.ndarray[np.int_]:
        array = np.array(self.data["data"], dtype=np.int_)
        array = array.reshape((self.height, self.width))
        if "-up" in self.render_order:
            array = array[::-1].copy()
        return array

    @property
    def objects(self) -> List[TiledMapObject]:
        if self._objects is None:
            self._objects = []
            if self.data.get("objects"):
                for obj in self.data["objects"]:
                    self._objects.append(TiledMapObject(self, obj))
        return self._objects

    def find_object_by_name(self, name: str) -> Optional[TiledMapObject]:
        for o in self.objects:
            if o.name == name:
                return o


class TiledMap:

    def __init__(
            self,
            filename: Union[str, Path],
    ):
        self.filename = Path(filename)
        self.data = json.loads(self.filename.read_text())
        self._layers: List[TiledMapLayer] = None

        self.render_order: str = self.data["renderorder"]
        self.width: int = self.data["width"]
        self.height: int = self.data["height"]
        self.size = (self.width, self.height)
        self.tile_width: int = self.data["tilewidth"]
        self.tile_height: int = self.data["tileheight"]
        self.tile_size = (self.tile_width, self.tile_height)
        self.pixel_width: int = self.data["width"] * self.tile_width
        self.pixel_height: int = self.data["height"] * self.tile_height
        self.pixel_size = (self.pixel_width, self.pixel_height)

    @property
    def layers(self):
        if self._layers is None:
            self._layers = []
            for i, l in enumerate(self.data["layers"]):
                self._layers.append(TiledMapLayer(self, i))
        return self._layers

