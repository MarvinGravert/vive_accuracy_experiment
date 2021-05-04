from modules.data_types import LaserPoint, VivePoint
from typing import List, Dict, Tuple
from more_itertools.more import combination_index, numeric_range, distinct_combinations
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm
from modules.build_data import get_vive_laser_points
from data_analysis import relative_distance_points, relative_angle_distance, range_based_error_calculation

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
    plt.figure(figsize=(8, 6), dpi=150)
    # popt, pcov = curve_fit(func, x, y)
    plt.xlabel('Winkelfehler [°]')
    plt.ylabel('Kumulative Häufigkeit')

    plt.title(f'Statische Genauigkeitsanalyse: Winkelfehler\n{acc}°\u00B1{std}°')
    # TODO: check naming kumulativer Fehler, evtl Verteilungsfunktion? siehe Normalverteilung
    print(len(x))
    plt.scatter(x, y, marker='o')
    # plt.plot(x, func(x, *popt), 'r-', label="Fitted Curve")
    plt.grid()
    # ticks
    ticky = list()
    for ti in chunked(x, 13):
        ticky.append(round(np.mean(ti), 0))
    # ticky = [20, 50, 80]
    # plt.xticks(np.linspace(start=min(x), stop=max(x), num=20, dtype=int))
    # accuracy line
    plt.vlines(acc, ymin=0, ymax=2, colors="r")
    ticky.append(acc)

    # add stuff
    plt.xticks(ticky)
    plt.ylim(ymin=0, ymax=1.05)
    plt.xlim(xmin=0)
    plt.show()


def cumultive_multi_experiment_plot_main():
    date_exp_num_layer_list = (("20201001", 1, [(0, 8), (9, 17), (18, 26)]),
                               ("20200918", 2, [(0, 8), (9, 17), (18, 25)]),
                               ("20200917", 2, [(0, 8), (9, 17), (18, 26)]),
                               ("20200918", 1, [(0, 8), ]))
    # date_exp_num_layer_list = (("20201001", 2, [(0,  34)]),
    #                            ("20200918", 3, [(0, 35)]),
    #                            ("20200917", 2, [(0, 34)]),
    #                            ("20200918", 1, [(0, 8), ]))
    # date_exp_num_layer_list = (("20201001", 2, [(27, 34)]),
    #                            ("20200918", 3, [(26, 35)]),
    #                            ("20200917", 2, [(27, 34)]),
    #                            )
    norm_length = 1500  # mm
    range_percentage = 0.05  # 5% .5
    # data preperation
    overall_error_list = list()
    overall_pair_list = list()
    overall_vive_points_list = list()
    for date, experiment_number, layer_list in date_exp_num_layer_list:
        vive_points, laser_points = get_vive_laser_points(date, experiment_number)
        overall_vive_points_list.extend(vive_points)
        for start_layer, end_layer in layer_list:

            error_list, pairs = range_based_error_calculation(vive_points=vive_points,
                                                              laser_points=laser_points,
                                                              norm_length=norm_length,
                                                              range_percentage=range_percentage,
                                                              start_point=start_layer,
                                                              end_point=end_layer)

            overall_error_list.extend(error_list)
            overall_pair_list.extend(pairs)
    #  Angle
    overall_error_list = np.rad2deg(overall_error_list)
    # Präzision
    precision = [x.std_position*1000 for x in overall_vive_points_list]
    precision_list = precision
    list_no_outliers = list()
    for e in overall_error_list:
        if e < 2:  # 2
            list_no_outliers.append(e)
    plot_cumultive_distribution(data_list=list_no_outliers)


def cumultive_smaller_workspace_plot_main():
    # for smaller workspace calculation
    date = "20201001"
    experiment_number = 2
    norm_length = 600  # mm
    range_percentage = 0.5  # 5%
    ##
    vive_points, laser_points = get_vive_laser_points(date, experiment_number)

    num_measurement_points = len(vive_points)
    measurement_points = list(range(27, 34))  # +[4, 13, 22]
    print(measurement_points)

    distinct_point_pairs = distinct_combinations(measurement_points, r=2)

    error_list, pairs = relative_distance_points(vive_points=vive_points,
                                                 laser_points=laser_points,
                                                 pair_list=distinct_point_pairs,
                                                 norm_length=norm_length,
                                                 range_percentage=range_percentage)
    print(len(error_list))
    # print(len(vive_points))
    # print(np.mean(error_list), "+-", np.std(error_list))
    print(pairs)
    plot_cumultive_distribution(data_list=error_list)


def cumultive_independent_layer_plot_main():
    # get data without influence from other layers (middle or upper)
    date = "20201001"
    experiment_number = 2
    norm_length = 600  # mm
    range_percentage = 0.15  # 5%
    ##
    vive_points, laser_points = get_vive_laser_points(date, experiment_number)

    overall_error_list = list()
    overall_pair_list = list()
    # for 18.09 as its missing the 18th => also 2 less error values
    # layer_list = [(0, 8), (9, 17), (18, 25)]
    # layer_list = [(0, 8), (9, 17), (18, 26)]  # full measurement set
    layer_list = [(27, 34)]
    for start_layer, end_layer in layer_list:

        error_list, pairs = range_based_error_calculation(vive_points=vive_points,
                                                          laser_points=laser_points,
                                                          norm_length=norm_length,
                                                          range_percentage=range_percentage,
                                                          start_point=start_layer,
                                                          end_point=end_layer)
        overall_error_list.extend(error_list)
        overall_pair_list.extend(pairs)
    print(overall_pair_list)
    print(len(overall_error_list))
    plot_cumultive_distribution(data_list=overall_error_list)


def cumultive_plot_main():
    date = "20200918"
    experiment_number = 1
    norm_length = 1500  # mm
    range_percentage = 0.03  # 5%
    # data preperation
    vive_points, laser_points = get_vive_laser_points(date, experiment_number)
    vive_points = vive_points[:]
    laser_points = laser_points[:]
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
    # cumultive_plot_main()
    # cumultive_independent_layer_plot_main()
    # cumultive_smaller_workspace_plot_main()
    cumultive_multi_experiment_plot_main()
