import unittest

import numpy as np

from src.util import triangulate


class TestTriangulation(unittest.TestCase):

    def test_100_read(self):
        res = triangulate([
            (0, 0), (10, 0), (10, 10),
                (20, 20), (10, 20), (0, 20),
        ])
        print(res)
