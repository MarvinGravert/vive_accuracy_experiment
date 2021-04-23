"""this module provides functionality for preprosscing laser and vive data
For the moment this only includes applying averaging for vive data and cutting
unneccessary values from laser data.
As a security check a checking function on the laser data has been implemented
which checks if the the first and last single point measurement taken by the
laser are near one oneanother (see the experiment process documentation)
"""
from typing import List, Tuple, Union

from utils.read_measurement_files import get_vive_points
import numpy as np
from loguru import logger


def average_vive_data(vive_data: List[np.ndarray]) -> List[np.ndarray]:
    """takes a list of individual vive measurements and returns a list containing
    the average across these measurement

    e.g.
        Input: List of 10 entries each containing 1000x7 matrix
        Output: List of 10 entries each containgin (7,) array

    TODO: Evaluate if its worth to apply quaternion averaging
    it shouldn't matter as we are considering a static process but worth considering
    for more accurateness


    Args:
        vive_data (List[np.ndarray]): List of vive measurements each containing a large matrix

    Returns:
        List[np.ndarray]: List of measurements averaged
    """
    return [np.mean(data, axis=0) for data in vive_data]


def std_vive_data(vive_data: List[np.ndarray]) -> List[np.ndarray]:
    return [np.std(vive_data, axis=0) for data in vive_data]


def cut_laser_data(laser_data: np.ndarray) -> np.ndarray:
    """cut the unnessceary parts of the laser data (such as temperature values)
    of the array as this information is not important
    As well as the first 5 rows as these were used for calibration

    Args:
        laser_data (np.ndarray): nx22 laser data

    Returns:
        np.ndarray: nx3 laser data
    """
    return laser_data[:, :3]


def check_tripod_moved(laser_data: np.ndarray, std=0.01) -> np.ndarray:
    """check if the tripod moved while collecting single point measurements from
    4 position
    This is done via comparing the first and fourth measurement as these are supposed
    to be at the same position while factorign in the 3 std interval
    Assumption is here that if the tripod has been moved this shuold

    If these are within a predefined range, an array containg only True is returned
    if they are not the entries a False is inserted

    returns an array the size equal the amount of measurement points

    Args:
        laser_data (np.ndarray): [description]

    Returns:
        np.ndarray: nx1 n:number of measurement position Those position that may have been affected
        are marked by a zero
    """
    # keep two list, once collecting the coordinate system origin position
    # once the control position
    # loop over the data starting at index 5 (0->4 used to build the coordinate system)
    # the control position
    init_pos_list = list()
    control_pos_list = list()
    for row_number in range(5, laser_data.shape[0], 4):
        init_pos_list.append(laser_data[row_number])
        control_pos_list.append(laser_data[row_number+3])
    # now compare for each axis => has_not_moved nx3 =>number measurement positionx 3 axis
    has_not_moved = np.isclose(init_pos_list, control_pos_list, atol=3*std)
    # now loop over all rows and those rows that contain a SINGLE False are saved
    # into another array as False aka this shouldnt be considered
    resulting_has_moved = np.ones((has_not_moved.shape[0], 1))
    for i, row in enumerate(has_not_moved):
        resulting_has_moved[i, :] = row.all()
    # atm 1 would signal not moved=>not super apparent=> invert
    return np.where((resulting_has_moved == 1) | (resulting_has_moved == 0),
                    1 - resulting_has_moved, resulting_has_moved)


def get_laser_std_deviation(laser_data: np.ndarray) -> List[float]:
    """returns the average std deviation across all samples a

        There is a stdTotal data field in the laser data. This is read out and
        the maximum retruned
        TODO: evaluate if this should rather be done per measured data point
        as or if the root mean squared should be used
    Args:
        laser_data (np.ndarray):

    Returns:
        List[float]: averaged std value
    """
    return max(laser_data[:, 6])
    # return np.mean(laser_data[:, 6])
    # return np.sqrt(np.mean(np.square(laser_data[:, 6]))) # root mean squared


def pre_process_laser(laser_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """pre process the laser data. This may include checking if the tripod was moved
    between the measurements (e.g. by accidently hitting it while moving the laser
    target from holder to holder)

    Args:
        laser_data (np.ndarray): nx22 containing the laser data

    Returns:
        Tuple[np.ndarray, np.ndarray]: pre processed laser data, array containing 1 where tripod
        may have been moved
    """
    std_laser = get_laser_std_deviation(laser_data)
    cut_data = cut_laser_data(laser_data)
    has_moved = check_tripod_moved(cut_data, std=std_laser)
    return cut_data, has_moved


def pre_process_vive(vive_data: List[np.ndarray]) -> List[np.ndarray]:
    """pre process vive data
    atm this is simply mean averaging

    Args:
        vive_data (List[np.ndarray]): [description]

    Returns:
        List[np.ndarray]: [description]
    """
    std_data = std_vive_data(vive_data)
    avg_data = average_vive_data(vive_data)
    return avg_data, std_data


def delete_corrupted_data(vive_data: List[np.ndarray],
                          laser_data: np.ndarray,
                          delete_arr: np.ndarray) -> Tuple[List[np.ndarray],
                                                           np.ndarray]:
    """delete data that could potentially been corrupted by having had the tripod moved

    delete_arr is a single dim array with 1 where data should be deleted.
    This measurement is deleted from vive and laser data

    Args:
        vive_data (List[np.ndarray]): List of measurements arrays
        laser_data (np.ndarray): laser measurements
        delete_arr (np.ndarray): single array containing 1 and 0

    Returns:
        Tuple[List[np.ndarray], np.ndarray]: vive and laser data having removed the
        measurements corresponding to 1
    """
    delete_index = np.argwhere(delete_arr.flatten())  # returns indices where array=1
    if delete_index.size == 0:
        return vive_data, laser_data
    logger.warning(f"deleting {delete_index=}")
    del vive_data[int(delete_index)]
    # Deleting laser is a bit more complex as we dont want to touch the inital coordinate frame
    # as well as having to delete 4 rows in the array and not just 1
    # essentially: ignore the first 5 entries, starting from the found index*4
    # go to the index*4+4 and delete those lines
    laser_delete_indices = list()
    for ind in delete_index:
        start = int(5+ind*4)
        stop = int(start+4)
        # list turns range into numbers (i know i can use list comprehension)
        laser_delete_indices.append(list(range(start, stop)))
    laser_data = np.delete(laser_data, laser_delete_indices, axis=0)
    return vive_data, laser_data


def pre_process_data(vive_data: List[np.ndarray],
                     laser_data: np.ndarray,
                     delete_data=False) -> Tuple[List[np.ndarray], List[np.ndarray], np.ndarray]:
    """processes the vive and laser data and returns averaged vive, its std and the prepared
    laser data. If set, data that may have been corrupted by having the tripod
    moved is deleted.

    Args:
        vive_data (List[np.ndarray]): vive data as read out from the measurement files
        laser_data (np.ndarray): laser data as read out from the measurement files
        delete_data (bool, optional): delete the potentially corrupted data. Defaults to False.

    Returns:
        Tuple[List[np.ndarray], List[np.ndarray], np.ndarray]: vive, std_vive,laser
    """
    proc_laser_data, tripod_moved = pre_process_laser(laser_data)
    if delete_data:
        vive_data, laser_data = delete_corrupted_data(vive_data, proc_laser_data, tripod_moved)
    proc_vive_data, std_vive = pre_process_vive(vive_data)
    return proc_vive_data, std_vive, laser_data


if __name__ == "__main__":
    from utils.read_measurement_files import get_laser_data
    laser_data = get_laser_data(date="20201001", experiment_number=1)
    vive_data = get_vive_points(date="20201001", experiment_number=1)

    vive, std_vive, laser = pre_process_data(vive_data=vive_data,
                                             laser_data=laser_data,
                                             delete_data=True)
