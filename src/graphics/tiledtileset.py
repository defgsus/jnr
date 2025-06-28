import dataclasses
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union, Optional, Dict, Tuple, Any

import moderngl


class TiledTileset:

    @dataclasses.dataclass
    class Tile:
        tileset: "TiledTileset"
        id: int
        x: int
        y: int
        type: Optional[str] = None


    @dataclasses.dataclass
    class Controller:
        tileset: "TiledTileset"
        id: int = 0
        flip_x: bool = False
        flip_y: bool = False

        @property
        def tile(self) -> Optional["TiledTileset.Tile"]:
            return self.tileset.mapping.get(self.id)

        def set_type(self, name: str):
            tile = self.tileset.mapping_by_type.get(name)
            if tile:
                self.id = tile.id

        def uniforms(self):
            return self.tileset.uniforms(self)


    def __init__(
            self,
    ):
        self.filename: Path = None
        self.image_filename: Path = None
        self.image_size: Tuple[int, int] = None
        self.tile_size: Tuple[int, int] = None
        self.map_size: Tuple[int, int] = None
        self.mapping: Dict[int, TiledTileset.Tile] = {}
        self.mapping_by_type: Dict[str, TiledTileset.Tile] = {}

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.filename.name}')"

    def create_controller(self):
        return self.Controller(self)

    @classmethod
    def open(cls, filename: Union[str, Path]):
        filename = Path(filename)
        et = ET.fromstring(filename.read_text())
        if et.tag != "tileset":
            raise ValueError(f"Expected `tileset` tag, got: `{et.tag}`")

        tileset = TiledTileset()
        tileset.filename = filename
        tileset.tile_size = (int(et.attrib["tilewidth"]), int(et.attrib["tileheight"]))
        tileset.map_size = (int(et.attrib["columns"]), int(et.attrib["tilecount"]) // int(et.attrib["columns"]))
        for elem in et:
            if elem.tag == "image":
                tileset.image_filename = filename.parent / elem.attrib["source"]
                tileset.image_size = (int(elem.attrib["width"]), int(elem.attrib["height"]))
            elif elem.tag == "tile":
                tile = cls.Tile(
                    tileset=tileset,
                    id=int(elem.attrib["id"]),
                    type=elem.attrib.get("type"),
                    x=int(elem.attrib["id"]) % int(et.attrib["columns"]),
                    y=int(elem.attrib["id"]) // int(et.attrib["columns"]),
                )
                tileset.mapping[int(elem.attrib["id"])] = tile
                if elem.attrib.get("type"):
                    tileset.mapping_by_type[elem.attrib["type"]] = tile

        if not tileset.image_filename:
            raise ValueError(f"Missing `image` tag in {filename}")

        return tileset

    def to_pil(self):
        from src.assets import assets
        return assets.get_image(self.image_filename)

    def uniforms(self, controller: Controller) -> Dict[str, Any]:
        tile = self.mapping[controller.id]
        scale_offset = [
            1. / self.map_size[0],
            1. / self.map_size[1],
            tile.x / self.map_size[0],
            (self.map_size[1] - 1 - tile.y) / self.map_size[1],
        ]
        if controller.flip_x:
            scale_offset[2] += scale_offset[0]
            scale_offset[0] *= -1
        if controller.flip_y:
            scale_offset[3] += scale_offset[3]
            scale_offset[1] *= -1

        return {
            "u_uv_scale_offset": scale_offset,
        }