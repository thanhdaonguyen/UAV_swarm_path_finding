from enum import Enum
import random
from input import *
random.seed(1)


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


def is_point_in_polygon(x, y, polygon):
    """Check if a point (x, y) is inside a polygon."""
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

class Map:
    """
        Map class to represent the map of the area of interest
        Attributes:
            aoi: Area of Interest, List of cell positition
            wind: Wind direction, Vector object
            num_of_obstacles: Number of obstacles to be rendered
            priority: 2D array to store the priority of each cell, dim: (map_width, map_height)
            state: 2D array to store the state of each cell, dim: (map_width, map_height)
            CellState: Enum to represent the state of a cell
    """
    class CellState:
        NOT_SCANNED = 1
        SCANNING = 3
        SCANNED = 2
        UNREACHABLE = -1
        NO_INTEREST = 0
    class DataState:
        NO_DATA = 0
        HAS_DATA = 1

    def __init__(self, aoi, num_of_obstacles, obstacles, map, uavs):
        self.aoi = aoi
        self.num_of_obstacles = num_of_obstacles
        self.priority = [[map[1][i][j] for j in range(map_height)] for i in range(map_width)]
        self.state = [[map[0][i][j] for j in range(map_height)] for i in range(map_width)]
        self.cluster_cells = []
        for cell in obstacles:
            self.state[cell[0]][cell[1]] = Map.CellState.UNREACHABLE



    def top_left_corner_of_the_cell(self, x, y):
        """
            Args:
                x: x-coordinate of the cell in the map
                y: y-coordinate of the cell in the map
            Returns:
                Point object representing the top left corner of the cell
        """
        return Point(x * cell_size, y * cell_size)

    def get_cell_position(self, point):
        """
            Args:
                point: Point object
            Returns:
                Tuple of cell position (x, y) of the given point
        """
        return (point.x // cell_size, point.y // cell_size) 
                    
    @classmethod
    def is_cluster_scanned(cls, map_state, cluster_center, cell_radius):
        """
        Check if the region within radius around cluster_center is fully scanned.
        """
        rows = len(map_state)
        cols = len(map_state[0])
        center_coor_x = cluster_center.x
        center_coor_y = cluster_center.y
        cls.cluster_cells = []


        for x in range(rows):
            for y in range(cols):
                cell_coor_x = x * cell_size + cell_size // 2
                cell_coor_y = y * cell_size + cell_size // 2
                radius = cell_radius * cell_size
                
                if (cell_coor_x - center_coor_x) ** 2 + (cell_coor_y - center_coor_y) ** 2 <= radius ** 2:
                    cls.cluster_cells.append((x, y))

        # print(cls.cluster_cells)

        for x in range(rows):
            for y in range(cols):
                cell_coor_x = x * cell_size + cell_size // 2
                cell_coor_y = y * cell_size + cell_size // 2
                radius = cell_radius * cell_size
                
                if (cell_coor_x - center_coor_x) ** 2 + (cell_coor_y - center_coor_y) ** 2 <= radius ** 2 and (map_state[x][y] == Map.CellState.NOT_SCANNED):
                    return False

        return True
