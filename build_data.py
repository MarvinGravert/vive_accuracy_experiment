from typing import List, Tuple

from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R
from more_itertools import chunked

from data_types import VivePoint, LaserPoint
from utils.linear_algebra_helper import transform_to_homogenous_matrix, build_coordinate_system_via_3_points
from utils.read_measurement_files import get_laser_data, get_vive_points
from pre_process_data import pre_process_data


def build_vive_points(vive_data: List[np.ndarray], std: np.ndarray) -> List[VivePoint]:
    vive_point_list = list()
    for measurement, measurement_std in zip(vive_data, std):
        if len(measurement) == 7:
            vive_point_list.append(
                VivePoint(
                    position=vive_data[: 3],
                    hom_matrix=transform_to_homogenous_matrix(
                        position=measurement[: 3],
                        quaternion=measurement[3:],
                        scalar_first=True
                    ),
                    std=measurement_std))
        elif len(measurement) == 12:
            hom_matrix = measurement.reshape((3, 4))
            hom_matrix = np.row_stack((hom_matrix, [0, 0, 0, 1]))
            position = hom_matrix[:3, 3]
            vive_point_list.append(VivePoint(
                position=position,
                hom_matrix=hom_matrix,
                std=measurement_std
            ))
        else:
            logger.error("Vive points dont have the correct format")
    return vive_point_list


def build_laser_points(laser_data: np.ndarray) -> List[LaserPoint]:
    # first 5 are useless => are the zero position, cut and place one empty
    laser_point_list = list()
    laser_data = laser_data[5:, :]
    laser_point_list.append(
        LaserPoint(
            position=[0, 0, 0],
            hom_matrix=np.identity(4)))
    for four_points in chunked(laser_data, 4):
        t = build_coordinate_system_via_3_points(*four_points[:-1])
        laser_point_list.append(LaserPoint(
            position=four_points[0],
            hom_matrix=t
        ))
    return laser_point_list


def get_vive_laser_points(date: str, experiment_number: int) -> Tuple[List[VivePoint],
                                                                      List[LaserPoint]]:
    laser_data = get_laser_data(date=date, experiment_number=experiment_number)
    vive_data = get_vive_points(date=date, experiment_number=experiment_number)
    vive, vive_std, laser = pre_process_data(vive_data, laser_data)
    # print(laser)
    laser_points = build_laser_points(laser_data=laser)
    vive_points = build_vive_points(vive_data=vive, std=vive_std)
    return vive_points, laser_points


if __name__ == "__main__":
    laser_data = get_laser_data(date="20201001", experiment_number=1)
    vive_data = get_vive_points(date="20201001", experiment_number=1)
    vive, vive_std, laser = pre_process_data(vive_data, laser_data)
    # print(laser)
    laser_points = build_laser_points(laser_data=laser)
    vive_points = build_vive_points(vive_data=vive, std=vive_std)
    # print(vive_std[0])
    # print(type(vive_std))
    print(vive_points[0])
