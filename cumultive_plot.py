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
    print(len(x))
    plt.scatter(x, y, marker='o')
    # plt.plot(x, func(x, *popt), 'r-', label="Fitted Curve")
    plt.grid()
    # ticks
    ticky = list()
    for ti in chunked(x, 15):
        ticky.append(round(np.mean(ti), 0))
    # plt.xticks(np.linspace(start=min(x), stop=max(x), num=20, dtype=int))
    plt.xticks(ticky)
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    plt.show()


def single_layer_data_plot(date,
                           experiment_number,
                           norm_length,
                           range_percentage,
                           start_layer,
                           end_layer) -> Tuple[List[float],
                                               Tuple[int, int]]:

    # data preperation
    vive_points, laser_points = get_vive_laser_points(date, experiment_number)

    # create only point pairs from the layers given

    distinct_point_pairs = distinct_combinations(range(start_layer, end_layer), r=2)

    error_list, pairs = relative_distance_points(vive_points=vive_points,
                                                 laser_points=laser_points,
                                                 pair_list=distinct_point_pairs,
                                                 norm_length=norm_length,
                                                 range_percentage=range_percentage)

    return error_list, pairs


def cumultive_layer_plot_main():
    print(len(overall_error_list))
    print(len(vive_points))
    for e, p in zip(overall_error_list, overall_pair_list):
        print(e, "  ", p)
    print(laser_points[9].position)
    print(laser_points[25].position)
    plot_cumultive_distribution(data_list=overall_error_list)


def cumultive_plot_main():
    date = "20200918"
    experiment_number = 2
    norm_length = 1500  # mm
    range_percentage = 0.03  # 5%
    # data preperation
    vive_points, laser_points = get_vive_laser_points(date, experiment_number)
    vive_points = vive_points[:26]
    laser_points = laser_points[:26]
    # processing
    num_measurement_points = len(vive_points)
    distinct_point_pairs = distinct_combinations(range(num_measurement_points), r=2)

    error_list, pairs = relative_distance_points(vive_points=vive_points,
                                                 laser_points=laser_points,
                                                 pair_list=distinct_point_pairs,
                                                 norm_length=norm_length,
                                                 range_percentage=range_percentage)
    # POST processing
    # # Angle
    # error_list = np.rad2deg(error_list)
    # Präzision
    # precision = [x.std_position*1000 for x in vive_points]
    # error_list = precision
    ########
    print(pairs)
    print(len(error_list))
    print(len(vive_points))
    print(np.mean(error_list), "+-", np.std(error_list))
    print(pairs)
    plot_cumultive_distribution(data_list=error_list)


if __name__ == "__main__":
    date = "20201001"
    experiment_number = 1
    norm_length = 1500
    # cumultive_plot_main()
    cumultive_layer_plot_main()
