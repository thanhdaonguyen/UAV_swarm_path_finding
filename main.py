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

# Initialize pygame
drawer = Drawer()
uavs = []
for i in range(num_of_uavs):
    uavs.append(UAV(random.uniform(0.9,1), 0, random.uniform(100, 200), None, Point(*uav_start), "./images/UAV.png"))
swarm = Swarm(uavs, Point(605, 445), "information")
map0 = Map(aoi, wind, num_of_obstacles, 10, uavs)
wavefront_map = wavefront((uav_end[0] // Parameters.cell_size, uav_end[1] // Parameters.cell_size), map0)
# print(wavefront_map)
uav_index = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
    
    num_of_busy_uavs = 0
    while uav_index < len(swarm.uavs) and swarm.uavs[uav_index].status == UAV.UAVState.BUSY:
        uav_index += 1
        if uav_index == len(swarm.uavs):
            uav_index = 0
        num_of_busy_uavs += 1
        if num_of_busy_uavs >= len(swarm.uavs):     
            break

    ###-----Main Algorithm-----###
    if swarm.uavs[uav_index].status == UAV.UAVState.FREE:
        uav_cell = swarm.uavs[uav_index].get_cell_position()
        #next_cell = find_nearest_cell(wavefront_map, uav_cell, map0)
        #print(next_cell)
        #shortest_path = find_shortest_path_to_next_cell(uav_cell, next_cell, map0)
        next_cell, shortest_path = find_path_to_nearest_cell_theta_star(wavefront_map, uav_cell, map0)
        if next_cell == None:
            swarm.uavs[uav_index].recent_path = None
            swarm.uavs[uav_index].target_position = None
        else:
            swarm.uavs[uav_index].recent_path = shortest_path
            swarm.uavs[uav_index].index_path = 0
            # print(swarm.uavs[uav_index].get_cell_position())
            swarm.uavs[uav_index].status = UAV.UAVState.BUSY
            map0.state[next_cell[0]][next_cell[1]] = Map.CellState.SCANNING
            # print(next_cell, shortest_path)
            swarm.uavs[uav_index].target_position = Point(next_cell[0] * Parameters.cell_size + Parameters.cell_size // 2, next_cell[1] * Parameters.cell_size + Parameters.cell_size // 2)

    swarm.move_a_frame()
    swarm.scan(map0)
    drawer.draw_all(map0, swarm)
    drawer.clock.tick(Parameters.FPS)
drawer.kill_window()

