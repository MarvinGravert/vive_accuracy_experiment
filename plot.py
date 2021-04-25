from modules.data_types import LaserPoint, VivePoint
from typing import List, Dict, Tuple
from more_itertools.more import numeric_range, distinct_combinations
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm
from modules.build_data import get_vive_laser_points
from data_analysis import relative_distance_points, relative_angle_distance

from more_itertools import chunked


def func(x, a, b, c):
    return a*np.log2(b+x)+c


def plot_cumultive_distribution(data_list: List[float]):
    n = len(data_list)
    x = np.sort(data_list)
    y = np.arange(n)/n

    acc = round(np.mean(data_list), 2)
    std = round(np.std(data_list), 2)
    # plotting
    # popt, pcov = curve_fit(func, x, y)
    plt.xlabel('Längenfehler [mm]')
    plt.ylabel('Kumulative Verteilung')

    plt.title(f'Statische Genauigkeitsanalyse: kumulativer Längenfehler\n{acc}+-{std}')

    plt.scatter(x, y, marker='o')
    # plt.plot(x, func(x, *popt), 'r-', label="Fitted Curve")
    plt.grid()
    # ticks
    ticky = list()
    for ti in chunked(x, 20):
        ticky.append(round(np.mean(ti), 0))
    # plt.xticks(np.linspace(start=min(x), stop=max(x), num=20, dtype=int))
    plt.xticks(ticky)
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    plt.show()


def cumultive_plot_main():
    date = "20200918"
    experiment_number = 3
    norm_length = 1500  # mm
    range_percentage = 0.1  # 5%
    # data preperation
    vive_points, laser_points = get_vive_laser_points(date, experiment_number)
    vive_points = vive_points[:]
    laser_points = laser_points[:]
    # processing
    num_measurement_points = len(vive_points)
    distinct_point_pairs = distinct_combinations(range(num_measurement_points), r=2)

    error_list, _ = relative_distance_points(vive_points=vive_points,
                                             laser_points=laser_points,
                                             pair_list=distinct_point_pairs,
                                             norm_length=norm_length,
                                             range_percentage=range_percentage)
    # POST processing
    # # Angle
    # error_list = np.rad2deg(error_list)
    # # Präzision
    # precision = [x.std_position for x in vive_points]
    # error_list = precision
    ########
    print(len(vive_points))
    print(np.mean(error_list), "+-", np.std(error_list))
    plot_cumultive_distribution(data_list=error_list)


if __name__ == "__main__":
    date = "20201001"
    experiment_number = 1
    norm_length = 1500
    cumultive_plot_main()
