

"""
    This file contains the input data for the simulation.
"""

aoi = [(6, 6), (12, 14), (20, 15), (29, 14), (32, 9), (28, 5), (21, 3), (13, 4)]
# aoi = [(6, 6), (12, 14), (21, 3), (13, 4)]
# aoi = [(6, 6), (12, 14), (29, 14), (32, 9),  (21, 3), (13, 4)]
# aoi = [(10, 10), (80, 14), (90, 40), (10, 35)]
num_of_obstacles = 30
num_of_uavs = 3
uav_start = (100, 100)
uav_end = (20, 10)

map_width = 40
map_height = 20
cell_size = 20
FPS = 60
cell_radius = 5
uav_distance = 130
time_charge = 300

min_speed = [100, 120, 140]
max_speed = [120, 140, 160]
dis_threshold = 100