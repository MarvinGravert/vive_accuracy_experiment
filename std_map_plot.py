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
from matplotlib.patches import Ellipse

import numpy.random as rnd


def func(x, a, b, c):
    return a*np.log2(b+x)+c


def map_std_plot(vive_points: List[VivePoint]):
    pos2d = [[v.position[0], v.position[2]] for v in vive_points]
    std2d = [[v.std_position[0], v.std_position[2]] for v in vive_points]

    pos2d = np.array(pos2d)
    std2d = np.array(std2d)
    ells = [Ellipse(xy=pos2d[i, :], width=std2d[i, 0]*1000, height=std2d[i, 1]*1000)
            for i in range(len(pos2d))]
    print(ells[0])
    pos2d = np.array(pos2d)
    fig = plt.figure(figsize=(8, 6), dpi=150)
    # popt, pcov = curve_fit(func, x, y)
    plt.xlabel('Winkelfehler [°]')
    plt.ylabel('Kumulative Häufigkeit')

    plt.title(f'Statische Genauigkeitsanalyse: Winkelfehler\n{2}°\u00B1{3}°')
    # TODO: check naming kumulativer Fehler, evtl Verteilungsfunktion? siehe Normalverteilung
    ax = plt.gca()

    for e in ells:
        ax.add_patch(e)
        # e.set_clip_box(ax.bbox)
        # e.set_alpha(rnd.rand())
        # e.set_facecolor(rnd.rand(3))
    # plt.scatter(pos2d[:, 0], pos2d[:, 1], marker='o')
    # plt.plot(x, func(x, *popt), 'r-', label="Fitted Curve")
    plt.grid()
    # ticks
    ax.set_xlim(-10, 10)

    ax.set_ylim(-10, 10)

    plt.show()


def cumultive_multi_experiment_plot_main():
    date_exp_num_layer_list = (("20201001", 1, [(0, 8)]),)
    #    ("20200918", 2, [(0, 8), (9, 17), (18, 25)]),
    #    ("20200917", 2, [(0, 8), (9, 17), (18, 26)]),
    #    ("20200918", 1, [(0, 8), ]))
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
        overall_vive_points_list.extend(vive_points[:8])
        for start_layer, end_layer in layer_list:

            error_list, pairs = range_based_error_calculation(vive_points=vive_points,
                                                              laser_points=laser_points,
                                                              norm_length=norm_length,
                                                              range_percentage=range_percentage,
                                                              start_point=start_layer,
                                                              end_point=end_layer)

            overall_error_list.extend(error_list)
            overall_pair_list.extend(pairs)

    map_std_plot(vive_points=overall_vive_points_list)


if __name__ == "__main__":
    # cumultive_plot_main()
    # cumultive_independent_layer_plot_main()
    # cumultive_smaller_workspace_plot_main()
    cumultive_multi_experiment_plot_main()
