from typing import List, Tuple

import adaptmesh
import numpy as np


def triangulate(points: List[Tuple[float, float]]):
    m = adaptmesh.triangulate(points, quality=.0)

    points = m.p.transpose()
    vertices = []
    for idx in m.t.transpose().flatten():
        vertices.append(points[idx])

    return np.stack(vertices)
