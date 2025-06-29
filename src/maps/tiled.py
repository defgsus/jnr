import json
from pathlib import Path
from typing import Union, Tuple

import numpy as np

class TiledMapObject:

    def __init__(self, layer: "TiledMapLayer", data: dict):
        self.layer = layer
        self.map = layer.map
        self.id = data["id"]
        self.x = data["x"]
        self.y = data["y"]
        self.draw_order = data["draworder"]
        self.map_x = self.x / self.map.width
        self.map_y = self.y / self.map.height

class TiledMapLayer:

    def __init__(self, map: "TiledMap", index: int):
        self.map = map
        self.index = index

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
        return self.map.data["renderorder"]

    def to_numpy(self) -> np.ndarray[np.int_]:
        array = np.array(self.data["data"], dtype=np.int_)
        array = array.reshape((self.height, self.width))
        if "-up" in self.render_order:
            array = array[::-1].copy()
        return array


class TiledMap:

    def __init__(
            self,
            filename: Union[str, Path],
    ):
        self.filename = Path(filename)
        self.data = json.loads(self.filename.read_text())

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
    def num_layers(self) -> int:
        return len(self.data["layers"])

    def layer(self, index: int) -> TiledMapLayer:
        return TiledMapLayer(self, index)

