import unittest

from src.graphics import TiledTileset
from src.assets import ASSET_PATH


class TestTiledTileset(unittest.TestCase):

    def test_100_read(self):
        tileset = TiledTileset.open(ASSET_PATH / "character-hero-ars-notoria-8x4-46x50.tsx")
        #print(tileset.mapping)
        self.assertEqual((46, 50), tileset.tile_size)
        self.assertEqual((8, 4), tileset.map_size)
        self.assertEqual((368, 200), tileset.image_size)

