from modules.data_types import LaserPoint, VivePoint
from typing import List, Dict, Tuple
from more_itertools.more import numeric_range
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm
from modules.build_data import get_vive_laser_points
from data_analysis import relative_distance_points

from more_itertools import chunked


def func(x, a, b, c):
    return a*np.log2(b+x)+c


def plot_cumultive_distribution(data_list: List[float]):
    n = len(data_list)
    x = np.sort(data_list)
    y = np.arange(n)/n
    # plotting
    # popt, pcov = curve_fit(func, x, y)
    plt.xlabel('Längenfehler [mm]')
    plt.ylabel('Kumulative Verteilung')

    plt.title('Statische Genauigkeitsanalyse: kumulativer Längenfehler')

    plt.scatter(x, y, marker='o')
    # plt.plot(x, func(x, *popt), 'r-', label="Fitted Curve")
    plt.grid()
    ticky = list()
    for ti in chunked(x, 18):
        ticky.append(int(np.mean(ti)))
    # plt.xticks(np.linspace(start=min(x), stop=max(x), num=20, dtype=int))
    plt.xticks(ticky)
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    plt.show()


def calc_relative_distance_error(vive_points: List[VivePoint],
                                 laser_points: List[LaserPoint],
                                 base_index: int,
                                 norm_length: float = 1500) -> List[float]:

    num_measurement_points = len(vive_points)
    col_0 = np.ones((num_measurement_points, 1), dtype=int)*base_index
    col_1 = np.arange(num_measurement_points).reshape((-1, 1))
    p_list = np.column_stack((col_0, col_1))

    return relative_distance_points(vive_points=vive_points,
                                    laser_points=laser_points,
                                    pair_list=p_list,
                                    norm_length=norm_length)


def cumultive_plot_main():
    date = "20201001"
    experiment_number = 1
    norm_length = 1500
    vive_points, laser_points = get_vive_laser_points(date, experiment_number)

    error_list = list()

    for i in range(len(vive_points)):
        error_list.extend(calc_relative_distance_error(vive_points,
                                                       laser_points,
                                                       i,
                                                       norm_length=norm_length))
    print(len(error_list))
    print(np.mean(error_list), "+-", np.std(error_list))
    plot_cumultive_distribution(data_list=error_list)


if __name__ == "__main__":
    date = "20201001"
    experiment_number = 1
    norm_length = 1500
    cumultive_plot_main()
