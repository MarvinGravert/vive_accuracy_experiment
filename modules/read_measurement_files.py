"""Modules to read in the measurement data from vive and laser

Vive data covers measurement and registration point. Both data is saved into a list, therein
the first (aka the zero) index refers to the registration point, though this naming is only 
kept around for legacy reason and may be changed later
"""
from typing import List

import numpy as np
import os
from pathlib import Path


def get_data_base_path() -> Path:
    return Path("./Experiment_Data")


def get_data_directory_path(date: str, experiment_number: int,) -> Path:
    """returns the path to the data which was taken during experiment number X
    on the specified date 

    Args:
        date (str): [description]
        experiment_number (int): [description]


    Returns:
        Path: [description]
    """
    base_path = get_data_base_path()
    return base_path / Path(date+f"_Exp{experiment_number}")


def read_vive_data(path2file):
    return np.loadtxt(path2file, delimiter=" ", skiprows=2)


def read_laser_data(path2file: Path) -> np.ndarray:
    return np.genfromtxt(path2file, delimiter=",", skip_header=1)


def get_laser_data(date: str, experiment_number: int) -> np.ndarray:
    """returns the raw laser data taken from X experiment on the specified date

    Args:
        date (str): yyyymmdd format 
        experiment_number (int): number of experiment

    Returns:
        np.ndarray: nx24 See the raw file to see the column specification
    """
    data_dir = get_data_directory_path(date=date, experiment_number=experiment_number)
    path2laser_file = data_dir/Path(f"{date}_Exp{experiment_number}_laserData.txt")
    return read_laser_data(path2laser_file)


def get_vive_points(date: str,
                    experiment_number: int,
                    ) -> List[np.ndarray]:
    """returns the data of all measurement points for
    the X Experiment on the specified date

    For legacy reason a registrationPoint.txt is read out

    Args:
        date (str): yyyymmdd format
        experiment_number (int): number of experiment
    Returns:
        List[np.ndarray]: list of numpy arrays each containing th emeasurements of one point
    """
    path2data = get_data_directory_path(date, experiment_number)
    counter = 1

    vive_measurement_point_list = list()
    """
    READ registration point
    """
    file_name = "registrationPoint.txt"
    file_path = path2data/Path(file_name)
    vive_measurement_point_list.append(read_vive_data(file_path))
    """
    READ measurement points
    """
    try:
        while True:
            file_name = f"measurementPoint{counter}.txt"
            file_path = path2data/Path(file_name)
            vive_measurement_point_list.append(read_vive_data(file_path))
            counter += 1

    except OSError:
        # happends when the file doesnt exist anymore
        pass
    return vive_measurement_point_list


if __name__ == "__main__":
    experimentNumber = "1"
    date = "20200827"

    v = get_vive_points(date, experimentNumber, registration_point=True)
    print(v)
