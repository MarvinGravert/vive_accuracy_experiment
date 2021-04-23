from typing import List
import numpy as np
from scipy.spatial.transform import Rotation as R

from .data_types import VivePoint, LaserPoint
from utils.linear_algebra_helper import transform_to_homogenous_matrix
from utils.read_measurement_files import get_laser_data, get_vive_points


def build_vive_points(vive_data: List[np.ndarray]) -> List[VivePoint]:
    pass


def build_laser_points(laser_data: np.ndarray) -> List[np.ndarray]:
    pass


if __name__ == "__main__":
    laser_data = get_laser_data(date="20201001", experiment_number=1)
    vive_data = get_vive_points(date="20201001", experiment_number=1)
