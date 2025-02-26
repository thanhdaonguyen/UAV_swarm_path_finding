num_of_busy_uavs = 0
    # while uav_index < len(swarm.uavs) and swarm.uavs[uav_index].status == UAV.UAVState.BUSY:
    #     uav_index += 1
    #     if uav_index == len(swarm.uavs):
    #         uav_index = 0
    #     num_of_busy_uavs += 1
    #     if num_of_busy_uavs >= len(swarm.uavs):     
    #         break

    # ###-----Main Algorithm-----###
    # if swarm.uavs[uav_index].status == UAV.UAVState.FREE:
    #     uav_cell = swarm.uavs[uav_index].get_cell_position()
    #     #next_cell = find_nearest_cell(wavefront_map, uav_cell, map0)
    #     #print(next_cell)
    #     #shortest_path = find_shortest_path_to_next_cell(uav_cell, next_cell, map0)
    #     next_cell, shortest_path = find_path_to_nearest_cell_theta_star(wavefront_map, uav_cell, map0, (test[i][0]//Parameters.cell_size, test[i][1]//Parameters.cell_size), Parameters.radius)
    #     if next_cell == None:
    #         swarm.uavs[uav_index].recent_path = None
    #         swarm.uavs[uav_index].target_position = None
    #     else:
    #         swarm.uavs[uav_index].recent_path = shortest_path
    #         swarm.uavs[uav_index].index_path = 0
    #         # print(swarm.uavs[uav_index].get_cell_position())
    #         swarm.uavs[uav_index].status = UAV.UAVState.BUSY
    #         map0.state[next_cell[0]][next_cell[1]] = Map.CellState.SCANNING
    #         # print(next_cell, shortest_path)
    #         swarm.uavs[uav_index].target_position = Point(next_cell[0] * Parameters.cell_size + Parameters.cell_size // 2, next_cell[1] * Parameters.cell_size + Parameters.cell_size // 2)

    # swarm.move_a_frame()