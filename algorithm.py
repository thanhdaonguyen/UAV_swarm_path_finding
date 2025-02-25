from Map import Map
from collections import deque
import numpy as np
import heapq

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
    state_map = np.array(map.state)
    rows, cols = state_map.shape
    result = [[-1 for _ in range(cols)] for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def bfs_condition(state_map, result, pos):
        x, y = pos
        return state_map[x][y] == Map.CellState.NOT_SCANNED and result[x][y] == -1

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
    if max(np.array(map.priority).flatten()) != 0:
        result += 1;
        result += np.array(map.priority) * max(result.flatten()) / max(np.array(map.priority).flatten())

    return result

def find_nearest_cell(wavefront_map, current_position, map):
    """
        Find the nearest cell from the current position
        Args:
            wavefront_map: 2D array representing the wavefront map
            current_position: Tuple of current position (x, y)
            map: Map object
        Returns:
            Tuple of nearest cell position (x, y)
    """

    state_map = np.array(map.state)
    rows, cols = state_map.shape
    shortest_path_map = [[-1 for _ in range(cols)] for _ in range(rows)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def bfs_condition(state_map, shortest_path_map, pos):
        x, y = pos
        return state_map[x][y] != Map.CellState.NO_INTEREST and state_map[x][y] != Map.CellState.UNREACHABLE and shortest_path_map[x][y] == -1

    pq = []
    heapq.heappush(pq, (0, current_position[0], current_position[1]))
    shortest_path_map[current_position[0]][current_position[1]] = 0

    result = -1
    cell = None
    while pq:
        dist, x, y = heapq.heappop(pq)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and bfs_condition(state_map, shortest_path_map, (nx, ny)):
                shortest_path_map[nx][ny] = dist + 1
                if state_map[nx][ny] == Map.CellState.NOT_SCANNED:
                    if result < wavefront_map[nx][ny]:
                        result = dist + 1
                        cell = (nx, ny)
                else:   
                    heapq.heappush(pq, (dist + 1, nx, ny))
    return cell

def find_path_to_nearest_cell_theta_star(wavefront_map, current_position, map):
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
        path.reverse()

    return cell, path