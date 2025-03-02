import random
from Map import Map
def generate_obstacles(num, map_width, map_height):
    return [(random.randint(0, map_width - 1), random.randint(0, map_height - 1)) for _ in range(num)]

def is_point_in_polygon(x, y, polygon):
    """Check if a point (x, y) is inside a polygon."""
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside
def generate_map(map_width, map_height, aoi, max_priority):
    """Tạo bản đồ trạng thái và mảng ưu tiên."""
    state_map = [[None] * map_height for _ in range(map_width)]
    priority_map = [[0] * map_height for _ in range(map_width)]

    for x in range(map_width):
        for y in range(map_height):
            if is_point_in_polygon(x, y, aoi):
                state_map[x][y] = Map.CellState.NOT_SCANNED
            else:
                state_map[x][y] = Map.CellState.NO_INTEREST

    for x in range(map_width):
        for y in range(map_height):
            if state_map[x][y] == Map.CellState.NOT_SCANNED:
                priority_map[x][y] = random.randint(1, max_priority)

    return state_map, priority_map
#==============================MAP======================================#
aoi_1 = [(6, 6), (12, 14), (20, 15), (29, 14), (32, 9), (28, 5), (21, 3), (13, 4)]
num_of_obstacles_1 = 30
map_width_1 = 40
map_height_1 = 20
cell_size_1 = 20
cell_radius_1 = 5
obstacles_1 = generate_obstacles(num_of_obstacles_1, map_width_1, map_height_1)
map_1 = generate_map(map_width_1, map_height_1, aoi_1, 10)
#====================Map2===========================#
aoi_2 = [(7, 7), (13, 15), (21, 16), (30, 15), (33, 10), (29, 6), (22, 4), (14, 5)]
num_of_obstacles_2 = 40
map_width_2 = 50
map_height_2 = 25
cell_size_2 = 25
cell_radius_2 = 6
obstacles_2 = generate_obstacles(num_of_obstacles_2, map_width_2, map_height_2)
map_2 = generate_map(map_width_2, map_height_2, aoi_2, 10)
#====================Map3===========================#
aoi_3 = [(8, 8), (14, 16), (22, 17), (31, 16), (34, 11), (30, 7), (23, 5), (15, 6)]
num_of_obstacles_3 = 50
map_width_3 = 60
map_height_3 = 30
cell_size_3 = 30
cell_radius_3 = 7
obstacles_3 = generate_obstacles(num_of_obstacles_3, map_width_3, map_height_3)
map_3 = generate_map(map_width_3, map_height_3, aoi_3, 10)
#=======================UAV============================#
# 3 UAVs
num_of_uavs_1 = 3
uav_start_1 = (100, 100)
uav_end_1 = (20, 10)
uav_distance_1 = 130
time_charge_1 = 300
min_speed_1 = [100, 120, 140]
max_speed_1 = [120, 140, 160]
dis_threshold_1 = 100

# 6 UAVs
num_of_uavs_2 = 6
uav_start_2 = (120, 120)
uav_end_2 = (15, 15)
uav_distance_2 = 150
time_charge_2 = 350
min_speed_2 = [110, 130, 150]
max_speed_2 = [130, 150, 170]
dis_threshold_2 = 110

# 9 UAVs
num_of_uavs_3 = 9
uav_start_3 = (140, 140)
uav_end_3 = (10, 20)
uav_distance_3 = 170
time_charge_3 = 400
min_speed_3 = [120, 140, 160]
max_speed_3 = [140, 160, 180]
dis_threshold_3 = 120

