from Parameters import CellState
from Parameters import Parameters
from utils import is_point_in_polygon


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
    def __init__(self, AoI, cell_size, wind_direction, wind_strength):
        self.cells = {}
        self.cell_size = cell_size
        self.wind_direction = wind_direction
        self.wind_strength = wind_strength

        step = Parameters.cell_size
        cell_size = Parameters.cell_size
        for x in range(0, Parameters.map_width, step):
            for y in range(0, Parameters.map_height, step):
                center_x = x + step // 2
                center_y = y + step // 2
                if is_point_in_polygon(center_x, center_y, AoI):
                    cell = Cell(x, y, 1, CellState.NOT_SCANNED, center_x, center_y)
                    self.cells[(center_x, center_y)] = cell
                else:
                    cell = Cell(x, y, 0, CellState.NO_INTEREST, center_x, center_y)
                    self.cells[(center_x, center_y)] = cell

    def update_state(self, new_points=None, new_cell_size=None, new_wind_direction=None, new_wind_strength=None):
        if new_points is not None:
            self.points = new_points
