from utils import Point, Vector
from Parameters import Parameters

"""
    This file contains the input data for the simulation.
"""

aoi = [(6, 6), (12, 14), (20, 15), (29, 14), (32, 9), (28, 5), (21, 3), (13, 4)]
num_of_obstacles = 90
num_of_uavs = 3
wind = Vector(2, 1)
uav_start = (6 * Parameters.cell_size, 6 * Parameters.cell_size)
uav_end = (29 * Parameters.cell_size, 14 * Parameters.cell_size)