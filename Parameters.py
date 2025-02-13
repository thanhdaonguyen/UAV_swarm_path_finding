from enum import Enum


class CellState(Enum):

    NOT_SCANNED = 0
    SCANNED = 1
    UNREACHABLE = 2
    UNKNOWN = 3
    NO_INTEREST = 4

class Parameters:
    map_width = 1200
    map_height = 800
    wind_direction = (0.5, 0.5)
    wind_strength = 10
    cell_size = 30

