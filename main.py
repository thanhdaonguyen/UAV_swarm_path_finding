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
from utils import find_circle_centers, centroid_priority
import Parameters

# Initialize pygame
drawer = Drawer()
map0 = Map(aoi, wind, num_of_obstacles)
uavs = []
for i in range(num_of_uavs):
    uavs.append(UAV(random.uniform(0.9,1), 0, random.uniform(100,200), None, Point(*uav_start), "./images/uav.png"))
cir_centers = find_circle_centers(map0.state)
circle_centers = []
for i in range(len(cir_centers)):
    circle_centers.append((cir_centers[i][0]*30, cir_centers[i][1]*30))
running = True
print(circle_centers)
start_time = time.time()
test = centroid_priority(map0.state, cir_centers, 5, 5)
for i in range(len(cir_centers)):
    test[i] = ((test[i][0]*30, test[i][1]*30))
print(test)
i = 0
swarm = Swarm(uavs, Point(test[0][0], test[0][1]), "information")
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
    swarm.uavs[0].set_direction(Vector(swarm.center.x - swarm.uavs[0].recent_position.x, swarm.center.y - swarm.uavs[0].recent_position.y))
    for uav in swarm.uavs:
        uav.move_a_frame()
    swarm.scan(map0)
    if (time.time() - start_time) > 5:
        # swarm.set_center(Point(circle_centers[i][0], circle_centers[i][1]))
        i += 1
        swarm.set_center(Point(test[i][0], test[i][1]))
        start_time = time.time()
    if swarm.get_center_cell_position() == swarm.uavs[0].get_cell_position():
        swarm.uavs[0].set_direction(Vector(0, 0))
    drawer.draw_all(map0, swarm, circle_centers)
drawer.kill_window()

