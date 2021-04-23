from dataclasses import dataclass, field
from typing import List

import numpy as np
from scipy.spatial.transform import Rotation as R


@dataclass
class DataPoint():
    position: List[float]
    # Rotation: Always from the point to the zero (either lighthouse or base KOS in laser
    quaternion: np.ndarray  # scalar first
    hom_matrix: np.ndarray


class VivePoint(DataPoint):
    std: float


class LaserPoint(DataPoint):
    pass
