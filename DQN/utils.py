from collections import namedtuple, deque
import random
import torch
import math
import heapq
import numpy as np

device = (
    torch.device(0)
    if torch.cuda.is_available()
    else torch.device("cpu")
)

Transition = namedtuple('Transition',
                        ('state_map', 'state_pos', 'action', 'next_state_map', 'next_state_pos', 'reward', 'terminal'))
class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, min(batch_size, len(self.memory)) - 1) + [self.memory[-1]]

    def __len__(self):
        return len(self.memory)
    
###---------------minimum enclosing circle-----------###
def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def is_in_circle(circle, p):
    if not circle:
        return False
    x, y, r = circle
    return dist((x, y), p) <= r

def circle_from_two(p1, p2):
    cx = (p1[0] + p2[0]) / 2
    cy = (p1[1] + p2[1]) / 2
    r = dist(p1, p2) / 2
    return (cx, cy, r)

def circle_from_three(p1, p2, p3):
    ax, ay = p1
    bx, by = p2
    cx, cy = p3
    
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if d == 0:
        return None
    
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    r = dist((ux, uy), p1)
    
    return (ux, uy, r)

def welzl(P, R=[]):
    if len(P) == 0 or len(R) == 3:
        if len(R) == 0:
            return None
        elif len(R) == 1:
            return (R[0][0], R[0][1], 0)
        elif len(R) == 2:
            return circle_from_two(R[0], R[1])
        elif len(R) == 3:
            return circle_from_three(R[0], R[1], R[2])

    p = P.pop()
    circle = welzl(P, R)
    
    if circle and is_in_circle(circle, p):
        P.append(p)
        return circle
    
    result = welzl(P, R + [p])
    P.append(p)
    return result

def min_enclosing_circle(points):
    points = points[:]  # Copy the list to avoid modifying the original
    random.shuffle(points)
    return welzl(points)
###---------------------------------------------###

def create_possible_move_map(map, radius):
    d = radius * 2
    possible_move_map = [[0 for i in range(len(map.state[0]))] for j in range(len(map.state))]

    next_points = []
    for x in range(len(map.state)):
        for y in range(len(map.state[0])):
            if map.state[x][y] == map.CellState.SCANNING:
                next_points.append((x, y))

    #print(next_points)
    center = [0, 0]
    #print(next_points)
    if(len(next_points) != 0):
        center[0], center[1], previous_radius = min_enclosing_circle(next_points)
        d = d - previous_radius
    
    #print(">>>>", center, radius)
    for x in range(len(map.state)):
        for y in range(len(map.state[0])):
            if map.state[x][y] == map.CellState.NOT_SCANNED:
                if len(next_points) == 0:
                    possible_move_map[x][y] = 1
                elif dist((x, y), center) <= d:
                    possible_move_map[x][y] = 1
    
    return possible_move_map

def get_state(swarm, uav_index, possible_move_map):
    uav_position = []
    #print(len(swarm.uavs))
    for uav in swarm.uavs:
      x, y = uav.get_cell_position()
      uav_position.append(x)
      uav_position.append(y)
    #print(uav_position)
    uav_position.append(uav_index)
    return possible_move_map, uav_position

### Theta Star ###

# Example Node class.
class Node:
    def __init__(self, x, y, g=float('inf'), parent=None):
        self.x = x
        self.y = y
        self.g = g
        self.parent = parent

    # Necessary for the heap to compare nodes based on cost.
    def __lt__(self, other):
        return self.g < other.g

def heuristic(a, b):
    """Euclidean distance as the heuristic."""
    return math.hypot(b[0] - a[0], b[1] - a[1])

def line_of_sight(grid, start, end, unreachable):
    """
    Uses Bresenham's algorithm to check if there's a clear line of sight
    between start and end in the grid. Returns False if any cell on the line
    is marked as 'unreachable'.
    """
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x1 >= x0 else -1
    sy = 1 if y1 >= y0 else -1
    err = dx - dy

    x, y = x0, y0
    while True:
        if grid[x][y] == unreachable:
            return False
        if (x, y) == (x1, y1):
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return True

def theta_star_path(start, map, goal):
    """Theta* pathfinding algorithm with improved unreachable handling."""
    grid = map.state
    rows, cols = len(grid), len(grid[0])
    
    # Create and initialize the start node.
    start_node = Node(*start, g=0)
    open_set = []
    heapq.heappush(open_set, (0, start_node))
    
    # Maintain a dictionary to hold one Node instance per (x, y)
    nodes = {start: start_node}

    while open_set:
        _, current = heapq.heappop(open_set)
        if (current.x, current.y) == goal:
            # Reconstruct path from goal to start.
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]

        # Check 4-connected neighbors; extend if needed.
        for dx, dy in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            nx, ny = current.x + dx, current.y + dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != map.CellState.UNREACHABLE:
                # Retrieve or create the neighbor node.
                if (nx, ny) in nodes:
                    neighbor = nodes[(nx, ny)]
                else:
                    neighbor = Node(nx, ny)  # Defaults to g=inf.
                    nodes[(nx, ny)] = neighbor

                # If a line of sight exists from current's parent to neighbor, use it.
                if current.parent and line_of_sight(
                        grid,
                        (current.parent.x, current.parent.y),
                        (nx, ny),
                        map.CellState.UNREACHABLE):
                    new_g = current.parent.g + heuristic((current.parent.x, current.parent.y), (nx, ny))
                    parent = current.parent
                else:
                    new_g = current.g + heuristic((current.x, current.y), (nx, ny))
                    parent = current

                if new_g < neighbor.g:
                    neighbor.g = new_g
                    neighbor.parent = parent
                    heapq.heappush(open_set, (new_g + heuristic((nx, ny), goal), neighbor))

    return None  # No path found.