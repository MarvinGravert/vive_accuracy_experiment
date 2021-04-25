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
    std_position: float = field(init=False)
    std_rotation: float = field(init=False)

    def __post_init__(self):
        if len(self.std) == 12:
            mat = self.std.reshape((3, 4))
            rot = mat[:3, :3]
            pos = mat[:3, 3]
            self.std_position = np.mean(pos)
            self.std_rotation = np.mean(rot)
        elif len(self.std) == 7:
            rot = self.std[3:]  # w i j k
            pos = self.std[:3]  # x y z
            self.std_position = np.mean(pos)
            self.std_rotation = np.mean(rot)


@dataclass
class LaserPoint(DataPoint):
    pass
