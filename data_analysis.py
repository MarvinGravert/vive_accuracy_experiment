from typing import Dict, Tuple, List, Union

import numpy as np
from scipy.linalg.misc import norm
from scipy.spatial.transform import Rotation as R

from utils.linear_algebra_helper import extract_position_and_quaternion_from_homogeneous_matrix
from modules.build_data import get_vive_laser_points
from modules.data_types import DataPoint, LaserPoint, VivePoint
from more_itertools import distinct_combinations

VIVE_CENTER_FROM_LASER = np.array([62, 62, 0])  # mm in laser coordinate system


def point_to_point_distance(start_system: DataPoint,
                            end_system: DataPoint,
                            point: np.ndarray = np.array([0, 0, 0])
                            ) -> float:
    """calculate the distance a point on the rigid connector moved between two measurement
    positions.
    The initial position is specified via start_system (in reference to the ground system
    e.g. either laser tracker or vive lighthouse). Within this system the point may
    be specified (if not its the origin of the coordinate system)

    using the transformation chain the distance can be calculated via the inverse
    of the hom_matrix of the end_system (the second position)

    Thus the point of interest (when it was located in the start_system) is known
    in the end_system, so the distance can be readily calculated

    Args:
        start_system (DataPoint): [description]
        end_system (DataPoint): [description]
        point_in_sys (np.ndarray, optional): [description]. Defaults to np.array([0, 0, 0]).

    Returns:
        float: [description]
    """
    point = np.append(point, 1).reshape((-1, 1))
    point_in_end = np.linalg.inv(
        end_system.hom_matrix)@start_system.hom_matrix@point
    diff = point.reshape((-1, 1))-point_in_end
    return np.linalg.norm(diff)


def relative_distance_points(vive_points: List[VivePoint],
                             laser_points: List[LaserPoint],
                             pair_list: Tuple[Tuple[int]],
                             norm_length: float = 1500,
                             range_percentage: float = 0.05) -> List[float]:
    """calculates the difference between the length reported by the laser and by the
    vive for the given pairs of measurement positions



    Args:
        vive_points (List[VivePoint]): positions as measured by the vive
        laser_points (List[LaserPoint]): positions as measured by the laser
        pair_list (Tuple[Tuple[int]]): measurement positions between those we distance shall be calculated
        norm_length (float, optional): distance of points which we are interested in (mm). Defaults to 1500.
        range_percentage (float, optional): range around the length of interest. Defaults to 0.05.

    Returns:
        List[float]: list of distance difference between the pairs, points pairs corresponding to the error
    """
    error_list = list()
    considered_pairs = list()
    lower_bound = norm_length*(1-range_percentage)
    upper_bound = norm_length*(1+range_percentage)
    for start, end in pair_list:
        laser_dist = point_to_point_distance(start_system=laser_points[start],
                                             end_system=laser_points[end],
                                             point=VIVE_CENTER_FROM_LASER)
        vive_dist = point_to_point_distance(vive_points[start],
                                            vive_points[end])
        if laser_dist > lower_bound and laser_dist < upper_bound:
            considered_pairs.append((start, end))
            error_list.append(abs(laser_dist-vive_dist*1000))

    return error_list, considered_pairs


def relative_angle_error(matrix):
    # note arccos can only return positive numbers
    return np.arccos((np.trace(matrix)-1)/2)


def relative_angle_distance(vive_points: List[VivePoint],
                            laser_points: List[LaserPoint],
                            pair_list: Tuple[Tuple[int]],
                            norm_length: float = 1500,
                            range_percentage: float = 0.05) -> List[float]:

    considered_pairs = list()
    error_list = list()
    lower_bound = norm_length*(1-range_percentage)
    upper_bound = norm_length*(1+range_percentage)
    for start, end in pair_list:
        laser_dist = point_to_point_distance(start_system=laser_points[start],
                                             end_system=laser_points[end],
                                             point=VIVE_CENTER_FROM_LASER)

        if laser_dist > lower_bound and laser_dist < upper_bound:
            # calc the hom matrix for moving from start->end in vive and laser
            vive_matrix = np.linalg.inv(
                vive_points[end].hom_matrix)@vive_points[start].hom_matrix
            laser_matrix = np.linalg.inv(
                laser_points[end].hom_matrix)@laser_points[start].hom_matrix
            # extract the angle from the rotation matrix
            vive_angle = relative_angle_error(vive_matrix[:3, :3])
            laser_angle = relative_angle_error(laser_matrix[:3, :3])
            # add pairs and angle difference
            considered_pairs.append((start, end))
            error_list.append(abs(vive_angle-laser_angle))

    return error_list, considered_pairs


def good_point_pairs(vive_points, laser_points):
    num_measurement_points = len(vive_points)

    distinct_point_pairs = list(distinct_combinations(range(num_measurement_points), r=2))

    error_list, pairs = relative_distance_points(vive_points=vive_points,
                                                 laser_points=laser_points,
                                                 pair_list=distinct_point_pairs)

    for e, p in zip(error_list, pairs):
        print(e, "  ", p)


if __name__ == "__main__":
    date = "20201001"
    experiment_number = 1
    vive_points, laser_points = get_vive_laser_points(date, experiment_number)

    num_measurement_points = len(vive_points)

    distinct_point_pairs = list(distinct_combinations(range(num_measurement_points), r=2))

    t = relative_angle_distance(vive_points=vive_points,
                                laser_points=laser_points,
                                pair_list=distinct_point_pairs)
    print(t)
    # good_point_pairs(vive_points[9:18], laser_points[9:18])
