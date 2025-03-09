import os 
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pygame
import sys
from input import *
from Map import Map, is_point_in_polygon
from UAV import UAV
from Swarm import Swarm
import random
from Drawer import Drawer
from utils import *
import time
from algorithm import *
from Measurer import Measurer
from trainRL import trainRL


measurer = Measurer(type = "rlUAV", num_of_uavs = num_of_uavs, map = maptype)
# Bước 1: Khởi tạo các thực thể, biến đếm
#drawer = Drawer("rlUAV")                       # Khởi tạo đối tượng Drawer
uavs = []                               # Khởi tạo danh sách các UAVs
for i in range(num_of_uavs):
    uavs.append(UAV(uav_distance.real, 0, time_charge,  min_speed[i], max_speed[i], None, Point(uav_start[0] * cell_size, uav_start[1] * cell_size), "./images/uav.png"))
swarm = Swarm(uavs, Point(605, 445))   # Khởi tạo đội Swarm
map0 = Map(state, priority)  # Khởi tạo đối tượng Map
uav_index = 0                          # Chỉ số của UAV hiện tại (Dùng để chọn UAV trong đội)

trainRL(map0, swarm, 5, (uav_start[0] * cell_size, uav_start[1] * cell_size), time_charge)
