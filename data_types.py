from dataclasses import dataclass, field
from typing import List

import numpy as np
from scipy.spatial.transform import Rotation as R


@dataclass
class DataPoint():
    position: List[float]
    # Rotation: Always from the point to the zero (either lighthouse or base KOS in laser
    hom_matrix: np.ndarray


@dataclass
class VivePoint(DataPoint):
    std: float


@dataclass
class LaserPoint(DataPoint):
    pass
