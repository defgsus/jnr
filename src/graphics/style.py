from typing import Optional, Union

import moderngl
import PIL.Image

from .tiledtileset import TiledTileset
from src.assets import assets


class Style:

    def __init__(
            self,
            texture_filename: Optional[str] = None,
            tileset_filename: Optional[str] = None,
    ):
        self.texture_filename = texture_filename
        self.tileset_filename = tileset_filename
        self._tileset = None
        self._tileset_controller = None

    @property
    def has_texture(self) -> bool:
        return bool(self.texture_filename or self.tileset_filename)

    @property
    def tileset(self) -> Optional[TiledTileset]:
        if self.tileset_filename and not self._tileset:
            self._tileset = assets.get_tiled_tileset(self.tileset_filename)
        return self._tileset

    @property
    def tileset_controller(self) -> Optional[TiledTileset.Controller]:
        if self.tileset_filename and not self._tileset_controller:
            self._tileset_controller = self.tileset.create_controller()
        return self._tileset_controller

    def to_pil(self) -> PIL.Image.Image:
        if self.tileset_filename:
            return self.tileset.to_pil()
        elif self.texture_filename:
            return assets.get_image(self.texture_filename)
        else:
            raise ValueError(f"Style has no texture")

    def to_texture_sampler(self, gl: moderngl.Context) -> moderngl.Sampler:
        # TODO: gl asset management
        image = self.to_pil()
        texture = gl.texture(image.size, 4, image.tobytes())
        sampler = gl.sampler(texture=texture)
        sampler.filter = (gl.LINEAR, gl.LINEAR)
        return sampler
