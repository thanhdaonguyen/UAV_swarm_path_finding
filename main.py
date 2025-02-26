import time
import pygame
from input import aoi, wind, num_of_obstacles, num_of_uavs, uav_start, uav_end
from Map import Map
from UAV import UAV
from Swarm import Swarm
from algorithm import wavefront, find_nearest_cell, find_path_to_nearest_cell_theta_star
import random
from Drawer import Drawer
from utils import Point
from Parameters import Parameters
from utils import find_circle_centers, centroid_priority

# Initialize pygame
drawer = Drawer()
uavs = []
for i in range(num_of_uavs):
    uavs.append(UAV(random.uniform(0.9,1), 0, random.uniform(100, 200), None, Point(*uav_start), "./images/UAV.png"))
swarm = Swarm(uavs, Point(605, 445), "information")
map0 = Map(aoi, wind, num_of_obstacles, 10, uavs)

wavefront_map = wavefront((uav_end[0] // Parameters.cell_size, uav_end[1] // Parameters.cell_size), map0)
uav_index = 0

cir_centers = find_circle_centers(map0.state)
circle_centers = []
for i in range(len(cir_centers)):
    circle_centers.append((cir_centers[i][0]*30, cir_centers[i][1]*30))
running = True

region_centers = centroid_priority(map0.state, cir_centers, 5, 5)
for i in range(len(region_centers)):
    region_centers[i] = (region_centers[i][0]*Parameters.cell_size, region_centers[i][1]*Parameters.cell_size)
# def distance(cell1, cell2):
#     return ((cell1[0] - cell2[0]) ** 2 + (cell1[1] - cell2[1]) ** 2) ** 0.5
#========================================================================================================#
#2 func này để tạm đây vì cho vô utils đang bị bug thiếu map, mà import map trong đó lại dính lỗi vòng lặp import
def swarm_at_center(swarm, region_center):
    """
    Check if all UAVs in the swarm are at the center of the region.
    """
    center_cell = (int(region_center.x // Parameters.cell_size), 
                   int(region_center.y // Parameters.cell_size))
    for uav in swarm.uavs:
        uav_cell = uav.get_cell_position()
        if uav_cell != center_cell:
            return False
    print(f"All UAVs at center: {center_cell}")
    return True

def is_region_scanned(wavefront_map, map_state, center_cell, radius):
    """
    Check if the region within radius around center_cell is fully scanned.
    """
    rows = len(map_state)
    cols = len(map_state[0])
    cx, cy = center_cell
    for x in range(int(max(0, cx - radius)), int(min(rows, cx + radius + 1))):
        for y in range(int(max(0, cy - radius)), int(min(cols, cy + radius + 1))):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2 and map_state[x][y] == Map.CellState.NOT_SCANNED:
                return False
    return True
#============================================================Main========================================#
running = True
current_region_index = 0
reached_center = False
i = 0
start_time = time.time()
swarm = Swarm(uavs, Point(region_centers[0][0], region_centers[0][1]), "information")

FPS = Parameters.FPS
while running and current_region_index < len(region_centers):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            running = False

    # Cập nhật tâm swarm cho khu vực hiện tại
    region_center = Point(*region_centers[current_region_index])
    swarm.set_center(region_center)
    center_cell = (int(region_center.x // Parameters.cell_size), int(region_center.y // Parameters.cell_size))
    # Đoạn này di chuyển swarm đến tâm khu vực (chỉ thực hiện một lần)
    if not reached_center:
        if not swarm_at_center(swarm, region_center):
            for uav in swarm.uavs:
                if uav.status == UAV.UAVState.FREE:
                    uav_cell = uav.get_cell_position()
                    next_cell, shortest_path = find_path_to_nearest_cell_theta_star(wavefront_map, uav_cell, map0, center_cell, Parameters.radius)
                    if next_cell != center_cell:
                        next_cell = center_cell 
                        shortest_path = [center_cell]
                    if next_cell:
                        uav.recent_path = shortest_path
                        uav.index_path = 0
                        uav.status = UAV.UAVState.BUSY
                        uav.target_position = Point(next_cell[0] * Parameters.cell_size + Parameters.cell_size // 2, 
                                                   next_cell[1] * Parameters.cell_size + Parameters.cell_size // 2)
                        print(f"UAV moving to center {next_cell} of region {current_region_index}")
        else:
            reached_center = True
            print(f"Swarm reached center of region {current_region_index}")

    # Quét khu vực sau khi đến tâm - tất cả uav phải đến tâm rồi mưới quét
    if reached_center:
        if is_region_scanned(wavefront_map, map0.state, center_cell, Parameters.radius):
            print(f"Region {current_region_index} scanned completely. Moving to next region.")
            current_region_index += 1
            reached_center = False
            if current_region_index >= len(region_centers):
                print("All regions scanned. Mission complete!")
                break
            continue

        # Phân công UAV quét trong khu vực
        for uav in swarm.uavs:
            if uav.status == UAV.UAVState.FREE or (uav.status == UAV.UAVState.BUSY and uav.recent_path is None):
                uav_cell = uav.get_cell_position()
                next_cell, shortest_path = find_path_to_nearest_cell_theta_star(wavefront_map, uav_cell, map0, center_cell, Parameters.radius)
                
                if next_cell is None:
                    print(f"UAV at {uav_cell}: No reachable cell in region {current_region_index}")
                    uav.recent_path = None
                    uav.target_position = None
                    uav.status = UAV.UAVState.FREE
                else:
                    uav.recent_path = shortest_path
                    uav.index_path = 0
                    uav.status = UAV.UAVState.BUSY
                    map0.state[next_cell[0]][next_cell[1]] = Map.CellState.SCANNING
                    uav.target_position = Point(next_cell[0] * Parameters.cell_size + Parameters.cell_size // 2, 
                                               next_cell[1] * Parameters.cell_size + Parameters.cell_size // 2)
                    print(f"UAV moving to {next_cell} in region {current_region_index}")

    swarm.move_a_frame()
    swarm.scan(map0)
    
    # Cập nhật trạng thái UAV sau khi di chuyển
    for uav in swarm.uavs:
        if uav.status == UAV.UAVState.BUSY and uav.recent_path and uav.index_path >= len(uav.recent_path):
            uav.recent_path = None
            uav.target_position = None
            uav.status = UAV.UAVState.FREE

    drawer.draw_all(map0, swarm, circle_centers)
    drawer.clock.tick(FPS)

# Kết thúc
drawer.kill_window()