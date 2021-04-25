import numpy as np
from more_itertools import distinct_combinations
import matplotlib.pyplot as plt
import networkx as nx

from modules.build_data import get_vive_laser_points
from data_analysis import relative_distance_points, relative_angle_distance


def main():
    date = "20201001"
    experiment_number = 1
    norm_length = 1500  # mm
    range_percentage = 0.1  # 5%
    # data preperation
    vive_points, laser_points = get_vive_laser_points(date, experiment_number)
    vive_points = vive_points[:9]
    laser_points = laser_points[:9]
    # processing
    num_measurement_points = len(vive_points)
    distinct_point_pairs = distinct_combinations(range(num_measurement_points), r=2)

    error_list, pairs = relative_distance_points(vive_points=vive_points,
                                                 laser_points=laser_points,
                                                 pair_list=distinct_point_pairs,
                                                 norm_length=norm_length,
                                                 range_percentage=range_percentage)
    return error_list, pairs, laser_points


err, pairs, laser_points = main()
G = nx.Graph()
for weight, edg in zip(err, pairs):
    G.add_edges_from([(*edg, {"weight": round(weight, 2)})])
print(G.nodes)
print(G.edges)
# nx.draw(G, with_labels=True, font_weight='bold')
# plt.show()


edges, weights = zip(*nx.get_edge_attributes(G, 'weight').items())

pos = {
    i: np.flip(point.position[:2]) for i, point in enumerate(laser_points)
}
nx.draw(G, pos, node_color='b', edgelist=edges, edge_color=weights, width=10.0,
        edge_cmap=plt.cm.Blues, with_labels=True, font_weight='bold')
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos,  edge_labels=labels)
plt.gca().invert_xaxis()
plt.show()
