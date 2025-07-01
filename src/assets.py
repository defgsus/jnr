from pathlib import Path
from typing import Dict, Any, Union

import PIL.Image

from src.graphics.tiledtileset import TiledTileset
from src.maps.tiledmap import TiledMap


ASSET_PATH = Path(__file__).resolve().parent.parent / "assets"

SEARCH_PATHS = [
    ASSET_PATH,
]


class Assets:

    def __init__(
            self,
    ):
        self._files: Dict[Path, Any] = {}

    def get_asset_filename(self, filename: Union[str, Path]):
        filename = Path(filename)
        if filename in self._files:
            return filename
        for path in SEARCH_PATHS:
            full_filename = path / filename
            if full_filename.exists():
                return full_filename
        raise FileNotFoundError(f"Asset not found: '{filename}'")

    def get_image(self, filename: Union[str, Path]) -> PIL.Image.Image:
        filename = Path(filename)
        full_filename = self.get_asset_filename(filename)
        if full_filename not in self._files:
            image = (
                PIL.Image.open(full_filename)
                .transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
                .convert("RGBA")
            )
            self._files[full_filename] = image
            self._files[filename] = image
        return self._files[full_filename]

    def get_tiled_map(self, filename: Union[str, Path]) -> TiledMap:
        filename = Path(filename)
        full_filename = self.get_asset_filename(filename)
        if full_filename not in self._files:
            map = TiledMap(full_filename)
            self._files[full_filename] = map
            self._files[filename] = map
        return self._files[full_filename]

    def get_tiled_tileset(self, filename: Union[str, Path]) -> TiledMap:
        filename = Path(filename)
        full_filename = self.get_asset_filename(filename)
        if full_filename not in self._files:
            tileset = TiledTileset.open(full_filename)
            self._files[full_filename] = tileset
            self._files[filename] = tileset
        return self._files[full_filename]


assets = Assets()
