import pygame
import sys
from input import aoi, wind, num_of_obstacles, num_of_uavs, uav_start, uav_end
from Map import Map, is_point_in_polygon
from UAV import UAV
from Swarm import Swarm
from utils import wavefront
import random
from utils import bfs
from Drawer import Drawer
from utils import *
import time
from Parameters import Parameters




# Bước 1: Khởi tạo các thực thể, biến đếm
drawer = Drawer()                       # Khởi tạo đối tượng Drawer
uavs = []                               # Khởi tạo danh sách các UAVs
for i in range(num_of_uavs):
    uavs.append(UAV(random.uniform(0.9,1), 120, 121, None, Point(*uav_start), "./images/uav.png"))
swarm = Swarm(uavs, Point(605, 445))   # Khởi tạo đội Swarm
map0 = Map(aoi, wind, num_of_obstacles, 10, uavs) # Khởi tạo đối tượng Map
# wavefront_map = wavefront((uav_end[0] // Parameters.cell_size, uav_end[1] // Parameters.cell_size), map0)
# wavefront_map = None
uav_index = 0                          # Chỉ số của UAV hiện tại (Dùng để chọn UAV trong đội)


# Bước 2: Các bước tiền tính toán
clusters_centers, clusters_available_cells = find_circle_centers_and_available_cells(map0)  # Tìm các tâm của các vùng cần quét
clusters_priority = calculate_centroid_priority(map0, clusters_centers, 5, 5)  # Tính toán ưu tiên của các vùng cần quét

# Bước 3: Vòng lặp chính

running = True
current_cluster_index = 0
reached_center = False
start_time = time.time()
swarm = Swarm(uavs, Point(clusters_priority[0][0], clusters_priority[0][1]))
FPS = Parameters.FPS

while running and current_cluster_index < len(clusters_priority):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            running = False

    # Cập nhật tâm swarm cho khu vực hiện tại
    current_cluster_center = Point(*clusters_priority[current_cluster_index])
    swarm.set_center(current_cluster_center)
    current_cluster_center_cell = Point(int(current_cluster_center.x // Parameters.cell_size), 
                                   int(current_cluster_center.y // Parameters.cell_size)
                                  )

    # Các UAV quét khu vực hiện tại
    if Map.is_cluster_scanned(map0.state, current_cluster_center, Parameters.radius):
        print(f"Region {current_cluster_index} scanned completely. Moving to next region.")
        current_cluster_index += 1
        if current_cluster_index >= len(clusters_priority):
            print("All regions scanned. Mission complete!")
            break
        
    
    # Phân công UAV quét trong khu vực
    for uav in swarm.uavs:
        if uav.status == UAV.UAVState.FREE or (uav.status == UAV.UAVState.BUSY and uav.recent_path is None):
            uav_cell_position = uav.get_cell_position()

            '''Lựa chọn cho các UAV tìm kiếm ô tiếp theo để quét dựa trên vị trí của cluster center hiện tại'''
            cluster_map = create_cluster_map(map0, clusters_available_cells[clusters_priority[current_cluster_index]])
            wavefront_map = wavefront((current_cluster_center_cell.x, current_cluster_center_cell.y), cluster_map)
            next_cell, shortest_path = select_target_cell(wavefront_map, uav_cell_position, cluster_map)
            '''Lựa chọn cho các UAV tìm kiếm ô tiếp theo để quét dựa trên vị trí hiện tại của UAV'''
            # wavefront_map = wavefront((uav_cell_position[0], uav_cell_position[1]), map0)
            # next_cell, shortest_path = select_target_cell(wavefront_map, Point(uav_cell_position[0], uav_cell_position[1]), map0)
            #print('path:', shortest_path)
            
            if next_cell is None: 
                #print(f"UAV at {uav_cell_position}: No reachable cell in region {current_cluster_index}")
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
                print(f"UAV moving to {next_cell} in cluster {current_cluster_index}")

    swarm.move_a_frame()
    swarm.scan(map0)
    
    # Cập nhật trạng thái UAV sau khi di chuyển
    for uav in swarm.uavs:
        if uav.status == UAV.UAVState.BUSY and uav.recent_path and uav.index_path >= len(uav.recent_path):
            uav.recent_path = None
            uav.target_position = None
            uav.status = UAV.UAVState.FREE

    drawer.draw_all(map0, swarm, clusters_centers, wavefront_map)
    drawer.clock.tick(FPS)

# Kết thúc
drawer.kill_window()