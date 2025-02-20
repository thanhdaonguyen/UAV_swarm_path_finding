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
    def __init__(self, AoI, cell_size, wind_direction, wind_strength, num_obstacles=10, valid_cells=None):
        self.cells = {}
        self.cell_size = cell_size
        self.wind_direction = wind_direction
        self.wind_strength = wind_strength
        self.valid_cells = []

        step = Parameters.cell_size
        cell_size = Parameters.cell_size
        valid_cells = []  # list valid cells for UAV to scan

        for x in range(0, Parameters.map_width, step):
            for y in range(0, Parameters.map_height, step):
                center_x = x + step // 2
                center_y = y + step // 2
                if is_point_in_polygon(center_x, center_y, AoI):
                    cell = Cell(x, y, 1, CellState.NOT_SCANNED, center_x, center_y)
                    self.cells[(center_x, center_y)] = cell
                    valid_cells.append([center_x, center_y, 1])  
                else:
                    cell = Cell(x, y, 0, CellState.NO_INTEREST, center_x, center_y)
                    self.cells[(center_x, center_y)] = cell
                    
        if len(valid_cells) >= num_obstacles:
            self.obstacles = random.sample(valid_cells, num_obstacles)
            for obstacle in self.obstacles:
                obs_x, obs_y, _ = obstacle  # Lấy tọa độ x, y từ danh sách
                if (obs_x, obs_y) in self.cells:
                    self.cells[(obs_x, obs_y)].update_value(-1)
                    self.cells[(obs_x, obs_y)].update_state(CellState.UNREACHABLE)
                
                # Cập nhật valid_cells để phản ánh rằng ô này là chướng ngại vật
                for cell in valid_cells:
                    if cell[0] == obs_x and cell[1] == obs_y:
                        cell[2] = -1  # Cập nhật giá trị của ô thành chướng ngại vật
                        break
        self.valid_cells = valid_cells
