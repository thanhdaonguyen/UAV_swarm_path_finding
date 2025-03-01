from collections import deque
import heapq
import numpy as np
from Map import Map
from input import *

class Point:
    """
        Point class to represent a point in the map
        Attributes:
            x: x-coordinate of the point in pixel
            y: y-coordinate of the point in pixel
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
class Cluster:
    """
        Cluster class to represent a cluster in the map
        Attributes:
            center: Point object representing the center of the cluster
            available_cells: List of available cells in the cluster
    """
    def __init__(self, center, available_cells, priority_avg):
        self.center = center
        self.available_cells = available_cells
        self.priority_avg = priority_avg
        self.end_of_cluster = None
    def distance_to(self, other):
        """Tính khoảng cách Euclidean giữa hai cluster"""
        return math.sqrt((self.center[0] - other.center[0])**2 + (self.center[1] - other.center[1])**2)

class Vector:
    """
        Vector class to represent a vector in the map
        Attributes:
            x: x-coordinate of the vector in pixel
            y: y-coordinate of the vector in pixel
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def normalize(self):
        """
            Normalize the vector
            Returns:
                Vector object representing the normalized vector
        """
        magnitude = (self.x ** 2 + self.y ** 2) ** 0.5
        if magnitude == 0:
            return Vector(0, 0)
        return Vector(self.x / magnitude, self.y / magnitude)

def get_sign(x):
    """
        Get the sign of a number
        Args:
            x: Number to get the sign
        Returns:
            1 if x >= 0, -1 otherwise
    """
    return -1 if x < 0 else 1


def bfs(valid_cells, start):
    # Tạo dictionary lưu trạng thái bản đồ
    map_dict = {(x, y): v for x, y, v in valid_cells}
    
    if start not in map_dict or map_dict[start] == -1:
        return None  # Điểm bắt đầu không hợp lệ

    # Khởi tạo ma trận khoảng cách (bắt đầu từ điểm start)
    distances = {pos: float('inf') for pos in map_dict if map_dict[pos] == 1}
    distances[start] = 0  # Khoảng cách đến chính nó là 0

    # Hàng đợi BFS, bắt đầu từ điểm start
    queue = deque([start])
    directions = [(0, 30), (0, -30), (30, 0), (-30, 0)]  # Lên, xuống, phải, trái
    
    while queue:
        x, y = queue.popleft()

        for dx, dy in directions:
            next_pos = (x + dx, y + dy)
            if next_pos in distances and distances[next_pos] == float('inf'):  # Chưa đi qua
                distances[next_pos] = distances[(x, y)] + 1
                queue.append(next_pos)
    return distances  # Trả về toàn bộ khoảng cách

### Tsunami algo ###
def wavefront(goal, map):
    """
        Calculate the wavefront map from the goal position
        Args:
            goal: Tuple of goal cell position (x, y)
            map: Map object
        Returns:
            2D array representing the wavefront map
    """
    state_map = map.state
    rows, cols = len(state_map), len(state_map[0])
    result = [[-1 for _ in range(cols)] for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def bfs_condition(state_map, result, pos):
        x, y = pos
        return state_map[x][y] != Map.CellState.UNREACHABLE and result[x][y] == -1

    pq = []
    heapq.heappush(pq, (0, goal[0], goal[1]))
    result[goal[0]][goal[1]] = 0

    while pq:
        dist, x, y = heapq.heappop(pq)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and bfs_condition(state_map, result, (nx, ny)):
                result[nx][ny] = dist + 1
                heapq.heappush(pq, (dist + 1, nx, ny))
    
    result = np.array(result, dtype=np.float32)
    # max_value_wavefront = max(result.flatten())

    # for i in range(rows):
    #     for j in range(cols):
    #         if state_map[i][j] != Map.CellState.UNREACHABLE:
    #             # print(state_map[x][y])
    #             result[i][j] = max_value_wavefront - result[i][j]

    # if max(np.array(map.priority).flatten()) != 0:
        # result += 1
        # result += np.array(map.priority) * max(result.flatten()) / max(np.array(map.priority).flatten())


    return result

import math

def have_cells_to_scan(center, map):
    """
    Check if there are cells to scan around the center of the region.
    """
    x, y = center
    radius = cell_radius * cell_size
    for i in range(len(map)):
        for j in range(len(map[0])):
            cell_coor_x = i * cell_size + cell_size / 2
            cell_coor_y = j * cell_size + cell_size / 2
            if (cell_coor_x - x) ** 2 + (cell_coor_y - y) ** 2 <= radius ** 2:
                if map[i][j] == Map.CellState.NOT_SCANNED:
                    return True
                
    return False
    

def find_circle_centers_and_available_cells(map):
    map = map.state
    radius = cell_radius * cell_size
    centers = []
    clusters=[]
    step_x = radius * math.sqrt(3)
    step_y = radius * 1.5

    # Xác định phạm vi chứa số 1
    xmin, ymin = map_height, map_width
    for i in range(len(map)):  
        for j in range(len(map[0])):  
            if map[i][j] == Map.CellState.NOT_SCANNED:
                xmin = min(xmin, i)
                ymin = min(ymin, j)

    
    # Duyệt theo dạng lưới lục giác
    # Chuyển các giới hạn x, y về dạng toạ độ trên canvas
    xmin = xmin * cell_size
    xmax = map_width * cell_size
    ymin = ymin  * cell_size + radius / 2
    ymax = map_height * cell_size

    x = xmin
    y = ymin
    while y <= ymax + radius:
        while x <= xmax + radius:
            if have_cells_to_scan((x, y), map):
                centers.append((x, y))
            x += step_x
        y += step_y
        x = xmin + step_x / 2 if ((y - ymin) / step_y) % 2 == 1 else xmin
        print("hahaahaha", (x - xmin) % step_x)
    

    # Tính các ô thuộc phạm vi của các center:
    for center in centers:
        x, y = center
        sum = 0
        available_cells = []
        for i in range(len(map)):
            for j in range(len(map[0])):
                cell_coor_x = i * cell_size + cell_size / 2
                cell_coor_y = j * cell_size + cell_size / 2
                if (cell_coor_x - x) ** 2 + (cell_coor_y - y) ** 2 <= radius ** 2:
                    # available_cells.append((cell_coor_x, cell_coor_y))
                    available_cells.append((i, j)) 
                    sum += map[i][j]
        priority_avg = sum / len(available_cells)
        cluster = Cluster(center, available_cells, priority_avg)
        clusters.append(cluster)
    # print(centers)
    return clusters

    
def calculate_centroid_priority(map):
    '''
    map: array with 0,1 value
    cen_circles: array store center, center is a tuple (x, y)
    time_to_scan: time that swarms have to scan the area that has centroid
    time_to_move: time that swarms have to move to the centroid
    return: array of centroid based on priority
    Tổng độ ưu tiên bằng tổng các ô trong vùng quét của centroid
    Ưu tiên tính bằng công thức: tổng ưu tiên/tổng thời gian di chuyển
    Thời gian di chuyển: time_to_move + time_to_scan
    priority = [(tổng ưu tiên) / (tổng số ô)] / (khoảng cách)
    '''
    # priority_list = []

    # for center in cen_circles:
    #     x, y = center
    #     total_priority = 0
    #     total_cells = 0
        
    #     for i in range(len(map.state)):
    #         for j in range(len(map.state[0])):
    #             cell_coor_x = i * cell_size + cell_size // 2
    #             cell_coor_y = j * cell_size + cell_size // 2
    #             radius = radius * cell_size
                
    #             if ((cell_coor_x - x) ** 2 + (cell_coor_y - y) ** 2 <= radius ** 2):
    #                 total_priority += map.priority[i][j]
    #                 total_cells += 1

    #     total_time = time_to_move + time_to_scan
    #     priority = total_priority / total_time if total_time > 0 else 0
    #     priority_list.append((center, priority))

    # priority_list.sort(key=lambda x: x[1], reverse=True)
    # # print(priority_list)
    # clusters_priority = [center for center, _ in priority_list]
    clusters = find_circle_centers_and_available_cells(map)
    sorted_clusters = sorted(clusters, key=lambda cluster: cluster.priority_avg, reverse=True)
    sorted_result = [sorted_clusters[0]]
    remaining_clusters = sorted_clusters[1:]


    '''Sắp xếp các cluster theo độ ưu tiên trung bình và khoảng cách so với cluster trước đó'''
    while remaining_clusters:
        prev_cluster = sorted_result[-1]
        next_cluster = max(
            remaining_clusters,
            key=lambda c: c.priority_avg / prev_cluster.distance_to(c)
        )
        sorted_result.append(next_cluster)
        remaining_clusters.remove(next_cluster)


    '''Tính toán điểm cuối của mỗi cluster'''
    for i in range(len(sorted_result) - 1):
        x1, y1 = sorted_result[i].center
        x2, y2 = sorted_result[i + 1].center
        dx = x2 - x1
        dy = y2 - y1
        magnitude = (dx ** 2 + dy ** 2) ** 0.5
        dx = dx / magnitude * cell_radius * cell_size
        dy = dy / magnitude * cell_radius * cell_size
        sorted_result[i].end_of_cluster = (x1 + dx, y1 + dy)
        
    sorted_result[-1].end_of_cluster = sorted_result[-1].center


    return sorted_result         #priority_list 
    # priority_list = []
    # for cluster in sorted_result:
    #     priority_list.append(cluster.center)
    # return priority_list #priority_list with only centers


def swarm_at_center(swarm, region_center):
    """
    Check if all UAVs in the swarm are at the center of the region.
    """
    center_cell = (int(region_center.x // cell_size), 
                   int(region_center.y // cell_size))
    for uav in swarm.uavs:
        uav_cell = uav.get_cell_position()
        if uav_cell != center_cell:
            return False
    print(f"All UAVs at center: {center_cell}")
    return True

def select_target_cell(wavefront_map, current_position, map):

    current_position = (current_position.x, current_position.y)
    
    def line_of_sight(map, start, end):
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while (x0, y0) != (x1, y1):
            if map.state[x0][y0] == Map.CellState.UNREACHABLE:
                return False
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return True

    def heuristic(a, b):
        """
            Heuristic function to calculate the distance between two points
            Args:
                a: Tuple of point a (x, y)
                b: Tuple of point b (x, y)
            Returns:
                Distance between two points
        """
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx ** 2 + dy ** 2) ** 0.5

    state_map = np.array(map.state)
    rows, cols = state_map.shape
    shortest_path_map = [[float('inf') for _ in range(cols)] for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def count_surround_not_NOT_SCANNED_cell(self, x, y):
        """
            Count the number of not NOT_SCANNED cell around the cell (x, y)
            Args:
                x: x-coordinate of the cell
                y: y-coordinate of the cell
            Returns:
                Number of not NOT_SCANNED cell around the cell
        """
        count = 0;
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and state_map[nx][ny] != Map.CellState.NOT_SCANNED:
                count += 1
        return count

    def bfs_condition(state_map, shortest_path_map, pos):
        x, y = pos
        return shortest_path_map[x][y] == float('inf') and state_map[x][y] != Map.CellState.UNREACHABLE

    pq = []
    heapq.heappush(pq, (0, current_position[0], current_position[1]))
    shortest_path_map[current_position[0]][current_position[1]] = 0
    parent_map = {current_position: current_position}
    print("current_position", current_position)

    min_cost = float('inf')
    result = -1
    cell = None
    num_of_max_surround_cell = 0
    while pq:
        dist, x, y = heapq.heappop(pq)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and bfs_condition(state_map, shortest_path_map, (nx, ny)):
                if line_of_sight(map, parent_map[(x, y)], (nx, ny)):
                    g_cost = shortest_path_map[x][y] + heuristic((x, y), (nx, ny))
                    if g_cost < shortest_path_map[nx][ny]:
                        shortest_path_map[nx][ny] = g_cost
                        parent_map[(nx, ny)] = parent_map[(x, y)]
                        if state_map[nx][ny] == Map.CellState.NOT_SCANNED:
                            if result <= wavefront_map[nx][ny] and min_cost >= g_cost:
                                if result == wavefront_map[nx][ny]:
                                    num_of_surround_cell = count_surround_not_NOT_SCANNED_cell(map, nx, ny)
                                    if num_of_max_surround_cell < num_of_surround_cell:
                                        num_of_max_surround_cell = num_of_surround_cell
                                        min_cost = g_cost
                                        result = wavefront_map[nx][ny]
                                        cell = (nx, ny)
                                else:
                                    num_of_max_surround_cell = 0
                                    min_cost = g_cost
                                    result = wavefront_map[nx][ny]
                                    cell = (nx, ny)
                        else:
                            heapq.heappush(pq, (g_cost + heuristic((nx, ny), current_position), nx, ny))
                else:
                    g_cost = shortest_path_map[x][y] + 1
                    if g_cost < shortest_path_map[nx][ny]:
                        shortest_path_map[nx][ny] = g_cost
                        parent_map[(nx, ny)] = (x, y)
                        if state_map[nx][ny] == Map.CellState.NOT_SCANNED:
                            if result <= wavefront_map[nx][ny] and min_cost >= g_cost:
                                if result == wavefront_map[nx][ny]:
                                    num_of_surround_cell = count_surround_not_NOT_SCANNED_cell(map, nx, ny)
                                    if num_of_max_surround_cell < num_of_surround_cell:
                                        num_of_max_surround_cell = num_of_surround_cell
                                        min_cost = g_cost
                                        result = wavefront_map[nx][ny]
                                        cell = (nx, ny)
                                else:
                                    num_of_max_surround_cell = 0
                                    min_cost = g_cost
                                    result = wavefront_map[nx][ny]
                                    cell = (nx, ny)
                        else:
                            heapq.heappush(pq, (g_cost + heuristic((nx, ny), current_position), nx, ny))
    
    # Reconstruct the path
    path = []
    if cell:
        current = cell
        while current != current_position:
            path.append(current)
            current = parent_map[current]
        # path.append(current_position)
        path.reverse()
    return cell, path

import copy
def create_cluster_map(original_map, cluster_available_cells):
    """
    Create a map with the same size as the original map but only contains the available cells in the cluster
    """

    cluster_map = copy.deepcopy(original_map)
    for x in range(len(cluster_map.state)):
        for y in range(len(cluster_map.state[0])):
            if (x, y) not in cluster_available_cells:
                if cluster_map.state[x][y] == Map.CellState.UNREACHABLE:
                    cluster_map.state[x][y] = Map.CellState.UNREACHABLE
                else:
                    cluster_map.state[x][y] = Map.CellState.NO_INTEREST 
    
    return cluster_map


# def select_target_cell(wavefront_map, current_position, map):

#     current_position = (current_position.x, current_position.y)
    
#     def line_of_sight(map, start, end):
#         x0, y0 = start
#         x1, y1 = end
#         dx = abs(x1 - x0)
#         dy = abs(y1 - y0)
#         sx = 1 if x0 < x1 else -1
#         sy = 1 if y0 < y1 else -1
#         err = dx - dy

#         while (x0, y0) != (x1, y1):
#             if map.state[x0][y0] == Map.CellState.UNREACHABLE:
#                 return False
#             e2 = 2 * err
#             if e2 > -dy:
#                 err -= dy
#                 x0 += sx
#             if e2 < dx:
#                 err += dx
#                 y0 += sy
#         return True

#     def heuristic(a, b):
#         """
#             Heuristic function to calculate the distance between two points
#             Args:
#                 a: Tuple of point a (x, y)
#                 b: Tuple of point b (x, y)
#             Returns:
#                 Distance between two points
#         """
#         dx = a[0] - b[0]
#         dy = a[1] - b[1]
#         return (dx ** 2 + dy ** 2) ** 0.5

#     state_map = np.array(map.state)
#     rows, cols = state_map.shape
#     shortest_path_map = [[float('inf') for _ in range(cols)] for _ in range(rows)]
#     directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
#     def count_surround_not_NOT_SCANNED_cell(self, x, y):
#         """
#             Count the number of not NOT_SCANNED cell around the cell (x, y)
#             Args:
#                 x: x-coordinate of the cell
#                 y: y-coordinate of the cell
#             Returns:
#                 Number of not NOT_SCANNED cell around the cell
#         """
#         count = 0;
#         for dx, dy in directions:
#             nx, ny = x + dx, y + dy
#             if 0 <= nx < rows and 0 <= ny < cols and state_map[nx][ny] != Map.CellState.NOT_SCANNED:
#                 count += 1
#         return count

#     def bfs_condition(state_map, shortest_path_map, pos):
#         x, y = pos
#         return shortest_path_map[x][y] == float('inf') and state_map[x][y] != Map.CellState.UNREACHABLE

#     pq = []
#     heapq.heappush(pq, (0, current_position[0], current_position[1]))
#     shortest_path_map[current_position[0]][current_position[1]] = 0
#     parent_map = {current_position: current_position}
#     print("current_position", current_position)

#     min_cost = float('inf')
#     result = -1
#     cell = None
#     num_of_max_surround_cell = 0
#     while pq:
#         dist, x, y = heapq.heappop(pq)
#         for dx, dy in directions:
#             nx, ny = x + dx, y + dy
#             if 0 <= nx < rows and 0 <= ny < cols and bfs_condition(state_map, shortest_path_map, (nx, ny)):
#                 if line_of_sight(map, parent_map[(x, y)], (nx, ny)):
#                     g_cost = shortest_path_map[x][y] + heuristic((x, y), (nx, ny))
#                     if g_cost < shortest_path_map[nx][ny]:
#                         shortest_path_map[nx][ny] = g_cost
#                         parent_map[(nx, ny)] = parent_map[(x, y)]
#                         if state_map[nx][ny] == Map.CellState.NOT_SCANNED:
#                             if result <= wavefront_map[nx][ny] and min_cost >= g_cost:
#                                 if result == wavefront_map[nx][ny]:
#                                     num_of_surround_cell = count_surround_not_NOT_SCANNED_cell(map, nx, ny)
#                                     if num_of_max_surround_cell < num_of_surround_cell:
#                                         num_of_max_surround_cell = num_of_surround_cell
#                                         min_cost = g_cost
#                                         result = wavefront_map[nx][ny]
#                                         cell = (nx, ny)
#                                 else:
#                                     num_of_max_surround_cell = 0
#                                     min_cost = g_cost
#                                     result = wavefront_map[nx][ny]
#                                     cell = (nx, ny)
#                         else:
#                             heapq.heappush(pq, (g_cost + heuristic((nx, ny), current_position), nx, ny))
#                 else:
#                     g_cost = shortest_path_map[x][y] + 1
#                     if g_cost < shortest_path_map[nx][ny]:
#                         shortest_path_map[nx][ny] = g_cost
#                         parent_map[(nx, ny)] = (x, y)
#                         if state_map[nx][ny] == Map.CellState.NOT_SCANNED:
#                             if result <= wavefront_map[nx][ny] and min_cost >= g_cost:
#                                 if result == wavefront_map[nx][ny]:
#                                     num_of_surround_cell = count_surround_not_NOT_SCANNED_cell(map, nx, ny)
#                                     if num_of_max_surround_cell < num_of_surround_cell:
#                                         num_of_max_surround_cell = num_of_surround_cell
#                                         min_cost = g_cost
#                                         result = wavefront_map[nx][ny]
#                                         cell = (nx, ny)
#                                 else:
#                                     num_of_max_surround_cell = 0
#                                     min_cost = g_cost
#                                     result = wavefront_map[nx][ny]
#                                     cell = (nx, ny)
#                         else:
#                             heapq.heappush(pq, (g_cost + heuristic((nx, ny), current_position), nx, ny))
    
#     # Reconstruct the path
#     path = []
#     if cell:
#         current = cell
#         while current != current_position:
#             path.append(current)
#             current = parent_map[current]
#         # path.append(current_position)
#         path.reverse()

#     return cell, path


def select_target_cell(wavefront_map, current_position, map):

    """
        Find the nearest cell from the current position using Theta* algorithm
        Args:
            wavefront_map: 2D array representing the wavefront map
            current_position: Tuple of current position (x, y)
            map: Map object
        Returns:
            Tuple of nearest cell position (x, y) and the path to the cell
    """
    
    def line_of_sight(map, start, end):
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while (x0, y0) != (x1, y1):
            if map.state[x0][y0] == Map.CellState.UNREACHABLE:
                return False
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return True

    def heuristic(a, b):
        """
            Heuristic function to calculate the distance between two points
            Args:
                a: Tuple of point a (x, y)
                b: Tuple of point b (x, y)
            Returns:
                Distance between two points
        """
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx ** 2 + dy ** 2) ** 0.5

    state_map = np.array(map.state)
    rows, cols = state_map.shape
    shortest_path_map = [[float('inf') for _ in range(cols)] for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def count_surround_not_NOT_SCANNED_cell(self, x, y):
        """
            Count the number of not NOT_SCANNED cell around the cell (x, y)
            Args:
                x: x-coordinate of the cell
                y: y-coordinate of the cell
            Returns:
                Number of not NOT_SCANNED cell around the cell
        """
        count = 0;
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and state_map[nx][ny] != Map.CellState.NOT_SCANNED:
                count += 1
        return count

    def bfs_condition(state_map, shortest_path_map, pos):
        x, y = pos
        return shortest_path_map[x][y] == float('inf') and state_map[x][y] != Map.CellState.UNREACHABLE

    pq = []
    heapq.heappush(pq, (0, current_position[0], current_position[1]))
    shortest_path_map[current_position[0]][current_position[1]] = 0
    parent_map = {current_position: current_position}
    #print("current_position", current_position)

    min_cost = float('inf')
    result = -1
    cell = None
    num_of_max_surround_cell = 0
    while pq:
        dist, x, y = heapq.heappop(pq)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and bfs_condition(state_map, shortest_path_map, (nx, ny)):
                if line_of_sight(map, parent_map[(x, y)], (nx, ny)):
                    g_cost = shortest_path_map[x][y] + heuristic((x, y), (nx, ny))
                    if g_cost < shortest_path_map[nx][ny]:
                        shortest_path_map[nx][ny] = g_cost
                        parent_map[(nx, ny)] = parent_map[(x, y)]
                        if state_map[nx][ny] == Map.CellState.NOT_SCANNED:
                            if result <= wavefront_map[nx][ny] and min_cost >= g_cost:
                                if result == wavefront_map[nx][ny]:
                                    num_of_surround_cell = count_surround_not_NOT_SCANNED_cell(map, nx, ny)
                                    if num_of_max_surround_cell < num_of_surround_cell:
                                        num_of_max_surround_cell = num_of_surround_cell
                                        min_cost = g_cost
                                        result = wavefront_map[nx][ny]
                                        cell = (nx, ny)
                                else:
                                    num_of_max_surround_cell = 0
                                    min_cost = g_cost
                                    result = wavefront_map[nx][ny]
                                    cell = (nx, ny)
                        else:
                            heapq.heappush(pq, (g_cost + heuristic((nx, ny), current_position), nx, ny))
                else:
                    g_cost = shortest_path_map[x][y] + 1
                    if g_cost < shortest_path_map[nx][ny]:
                        shortest_path_map[nx][ny] = g_cost
                        parent_map[(nx, ny)] = (x, y)
                        if state_map[nx][ny] == Map.CellState.NOT_SCANNED:
                            if result <= wavefront_map[nx][ny] and min_cost >= g_cost:
                                if result == wavefront_map[nx][ny]:
                                    num_of_surround_cell = count_surround_not_NOT_SCANNED_cell(map, nx, ny)
                                    if num_of_max_surround_cell < num_of_surround_cell:
                                        num_of_max_surround_cell = num_of_surround_cell
                                        min_cost = g_cost
                                        result = wavefront_map[nx][ny]
                                        cell = (nx, ny)
                                else:
                                    num_of_max_surround_cell = 0
                                    min_cost = g_cost
                                    result = wavefront_map[nx][ny]
                                    cell = (nx, ny)
                        else:
                            heapq.heappush(pq, (g_cost + heuristic((nx, ny), current_position), nx, ny))
    
    # Reconstruct the path
    path = []
    if cell:
        current = cell
        while current != current_position:
            path.append(current)
            current = parent_map[current]
        path.append(current_position)
        path.reverse()
    path_to_charge = []
    cell_charge = (10, 10)
    if cell_charge:
        current = cell_charge
        while current != current_position:
            path_to_charge.append(current)
            current = parent_map[current]
        path_to_charge.append(current_position)
        path_to_charge.reverse()
    return cell, path, path_to_charge

import copy
def create_cluster_map(original_map, cluster_available_cells):
    """
    Create a map with the same size as the original map but only contains the available cells in the cluster
    """

    cluster_map = copy.deepcopy(original_map)
    for x in range(len(cluster_map.state)):
        for y in range(len(cluster_map.state[0])):
            if (x, y) not in cluster_available_cells:
                if cluster_map.state[x][y] == Map.CellState.UNREACHABLE:
                    cluster_map.state[x][y] = Map.CellState.UNREACHABLE
                else:
                    cluster_map.state[x][y] = Map.CellState.NO_INTEREST 
    
    return cluster_map

def cal_distance_path(path):
    dis = 0
    for i in range(1, len(path)):
        dis += ((path[i][0] - path[i-1][0])**2 + (path[i][1] - path[i-1][1]))**0.5
    return dis