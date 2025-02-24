import time
import pygame
import sys
from input import aoi, wind, num_of_obstacles, num_of_uavs, uav_start, uav_end
from Map import Map
from UAV import UAV
from Swarm import Swarm
import random
from utils import bfs
from Drawer import Drawer
from utils import Point, Vector
from utils import find_circle_centers
import Parameters

# Initialize pygame
drawer = Drawer()
map0 = Map(aoi, wind, num_of_obstacles)
uavs = []
for i in range(num_of_uavs):
    uavs.append(UAV(random.uniform(0.9,1), 0, random.uniform(100,200), None, Point(*uav_start), "./images/uav.png"))
swarm = Swarm(uavs, Point(605, 445), "information")
swarm.uavs[0].set_direction(Vector(swarm.center.x - swarm.uavs[0].recent_position.x, swarm.center.y - swarm.uavs[0].recent_position.y))
circle_centers = find_circle_centers(map0.state)
running = True
print(circle_centers)
start_time = time.time()
i = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
    for uav in swarm.uavs:
        uav.move_a_frame()
    swarm.scan(map0)
    if (time.time() - start_time) > 5:
        swarm.set_center((circle_centers[i][0]*30, circle_centers[i][1]*30))
        start_time = time.time()
        i += 1
    if swarm.get_center_cell_position() == swarm.uavs[0].get_cell_position():
        swarm.uavs[0].set_direction(Vector(0, 0))
    drawer.draw_all(map0, swarm, circle_centers)
drawer.kill_window()

