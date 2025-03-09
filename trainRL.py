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
from DQN.Agent import Agent
from DQN.utils import theta_star_path
import copy
import time 

def trainRL(map, swarm, radius, recent_position, time_charge):
    first_map = map
    print("start")
    measurer = Measurer(type = "training-RL")

    global_agent = Agent(swarm)

    # for uav in swarm.uavs: 
    #     print(uav.get_cell_position())
    #     uav.agent = Agent(swarm)

    result_swarm = swarm
    drawer = Drawer("rlUAV")  

    print("end")
    f = open('output.txt', 'w')
    step = 1000
    e = 0.9
    for i in range(step):
        e = max(0.9 * e, 0.2)
        t11 = time.time()
        map = copy.deepcopy(first_map)
        swarm = copy.deepcopy(result_swarm)
        
        # for index in range(len(swarm.uavs)): 
        #     swarm.uavs[index].time_charge = copy.deepcopy(time_charge)
        #     swarm.uavs[index].recent_position = Point(*recent_position)
        #     swarm.uavs[index].target_position = None
        #     swarm.uavs[index].recent_path = None
        #     swarm.uavs[index].status = UAV.UAVState.FREE
        #     swarm.uavs[index].is_blocked = 0

        # for x in range(len(map.state)):
        #     for y in range(len(map.state[0])):
        #         if map.state[x][y] == map.CellState.SCANNED:
        #             map.state[x][y] = map.CellState.NOT_SCANNED
        count = 0;
        measurer = Measurer(type = "training-RL")
        for x in range(len(map.state)):
            for y in range(len(map.state[0])):
                if map.state[x][y] == map.CellState.NOT_SCANNED:
                    count += 1;

        t12 = time.time()
        print(f"time: {t12 - t11}")

        # swarm.uavs[0].agent.create_possible_map(map, radius)
        # swarm.uavs[0].agent.set_state(swarm)
        # previous_state = swarm.uavs[0].agent.state

        # global_agent.create_possible_map(map, radius)
        # global_agent.set_state(swarm, 0)
        previous_state = None
        previous_next_cell = None
        previous_reward_point = 0
        uav_index = 0
        running = True
        while running:
            t1 = time.time()
            cnt_blocked_uavs = 0
            for uav in swarm.uavs:
                if uav.is_blocked == 1:
                    uav.time_charge -= 1
                    #print(uav.time_charge)
                    cnt_blocked_uavs += 1;
                    if  uav.time_charge == 0:
                        cnt_blocked_uavs -= 1;
                        uav.is_blocked = 0
                        uav.distance= uav_distance
                        uav.time_charge = time_charge
                        uav.status = UAV.UAVState.FREE

            #print(uav_index)
            if cnt_blocked_uavs != len(swarm.uavs):
                num_of_busy_uavs = 0
                while uav_index < len(swarm.uavs) and swarm.uavs[uav_index].status == UAV.UAVState.BUSY:
                    uav_index += 1
                    if uav_index == len(swarm.uavs):
                        uav_index = 0
                    num_of_busy_uavs += 1
                    if num_of_busy_uavs >= len(swarm.uavs):     
                        break
                    
                    #print(swarm.uavs[uav_index].status)
            recent_uav = swarm.uavs[uav_index]
            
            
            #print(uav_index)
            ###-----Main Algorithm-----###
            if recent_uav.status == UAV.UAVState.FREE:
                #print("show", count)
                if count <= 0: 
                    break
                #print(uav_index, "???")
                t2 = time.time()
                uav_cell_position = recent_uav.get_cell_position()
                # recent_uav.agent.create_possible_map(map, radius)
                # recent_uav.agent.set_state(swarm)
                # next_cell = recent_uav.agent.exploration(e)

                global_agent.create_possible_map(map, radius)
                global_agent.set_state(swarm, uav_index)
                next_cell = global_agent.exploration(e)
                
                t3 = time.time()
                #print(next_cell)
                if next_cell != 1:
                    #count -= 1;
                    
                    shortest_path = theta_star_path(uav_cell_position, map, next_cell)
                    t4 = time.time()
                    ###################Train##################
                    if previous_state == None:
                        previous_state = global_agent.state
                        previous_next_cell = next_cell
                    else:
                        _, previous_state = global_agent.iter(previous_state, previous_next_cell, previous_reward_point - measurer.reward_point, 999999999999999 if measurer.cost == 0 else 1 / measurer.cost)
                        previous_next_cell = next_cell
                    #_, previous_state = recent_uav.agent.iter(previous_state, next_cell, measurer.reward_point - previous_reward_point, measurer.reward_point)
                    # if uav_index == 1:
                    #     print(f"loss:{_}")
                    #     print(f"reward: {measurer.reward_point - previous_reward_point}")
                    previous_reward_point = measurer.reward_point
                    
                    t5 = time.time()
                    recent_uav.recent_path = shortest_path
                    recent_uav.index_path = 0
                    recent_uav.status = UAV.UAVState.BUSY
                    map.state[next_cell[0]][next_cell[1]] = Map.CellState.SCANNING
                    recent_uav.target_position = Point(next_cell[0] * cell_size + cell_size // 2, 
                                                next_cell[1] * cell_size + cell_size // 2)
                    dis = cal_distance_path(recent_uav.recent_path)
                    recent_uav.distance -= dis
                    if recent_uav.distance.real < dis_threshold:
                            map.state[next_cell[0]][next_cell[1]] = Map.CellState.NOT_SCANNED
                            recent_uav.is_blocked = 1
                            recent_uav.index_path = 0
                            recent_uav.recent_path = theta_star_path(uav_cell_position, map, base)

                    t6 = time.time()
            if cnt_blocked_uavs != len(swarm.uavs):
                swarm.move_a_frame()
                priority_total, priority_count = swarm.scan(map)
                count -= priority_count
                measurer.add_cost(priority_total)
            measurer.tick_time()
            t7 = time.time()

            #print(f"time: {t2 - t1}, {t3 - t2}, {t4 - t3}, {t5 - t4}, {t6 - t5}, {t7 - t6}")
            

            drawer.draw_all(map, swarm)
            drawer.clock.tick(FPS)
        # t11 = time.time()
        # for index in range(len(result_swarm.uavs)): 
        #     #print(result_swarm.get_cell_position())
        #     result_swarm.uavs[index].agent = copy.deepcopy(swarm.uavs[index].agent)  
        # t12 = time.time()
        # print(f"time: {t12 - t11}")
        print(f"final_cost in step {i}: {measurer.cost}")
        print(f"final_reward_point in step {i}: {measurer.reward_point}")
        f.write(f"{measurer.cost}, ")