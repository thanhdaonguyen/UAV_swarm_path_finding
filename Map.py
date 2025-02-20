from Parameters import CellState
from Parameters import Parameters
from utils import is_point_in_polygon
import random

class Cell:
    def __init__(self, x, y, value, state=CellState.UNKNOWN, center_x=None, center_y=None):
        self.x = x
        self.y = y
        self.value = value
        self.state = state
        self.center_x = center_x
        self.center_y = center_y

    def update_value(self, new_value):
        self.value = new_value
    
    def update_state(self, new_state):
        self.state = new_state

    def __str__(self):
        return f"x: {self.x}, y: {self.y}, value: {self.value}"

class Map:
    def __init__(self, AoI, cell_size, wind_direction, wind_strength, num_obstacles=10):
        self.cells = {}
        self.cell_size = cell_size
        self.wind_direction = wind_direction
        self.wind_strength = wind_strength

        step = Parameters.cell_size
        cell_size = Parameters.cell_size
        valid_cells = []  # list valid cells for UAV to scan

        for x in range(0, Parameters.map_width, step):
            for y in range(0, Parameters.map_height, step):
                center_x = x + step // 2
                center_y = y + step // 2
                if is_point_in_polygon(center_x, center_y, AoI):
                    valid_cells.append((center_x, center_y))
                    cell = Cell(x, y, 1, CellState.NOT_SCANNED, center_x, center_y)
                    self.cells[(center_x, center_y)] = cell
                else:
                    cell = Cell(x, y, 0, CellState.NO_INTEREST, center_x, center_y)
                    self.cells[(center_x, center_y)] = cell
                    
        # Randomly place obstacles
        if len(valid_cells) >= num_obstacles:
            self.obstacles = random.sample(valid_cells, num_obstacles)
            for obs_x, obs_y in self.obstacles:
                cell = Cell(obs_x - step // 2, obs_y - step // 2, -1, CellState.UNREACHABLE, obs_x, obs_y)
                self.cells[(obs_x, obs_y)] = cell
