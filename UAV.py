from utils import Vector, get_sign
from Parameters import Parameters
from enum import Enum
from Map import Map
import random

class UAV:
    """
        UAV class to represent a UAV
        Attributes:
            remain_energy: Remaining energy of the UAV
            status: Status of the UAV (FREE or BUSY)
            min_speed: Minimum speed of the UAV
            max_speed: Maximum speed of the UAV
            buffer_data: Buffer data of the UAV
            recent_position: Recent position of the UAV in pixel
            target_position: Target position of the UAV in pixel
            direction: Direction of the UAV (Vector object which was normalized)
            recent_path: Recent path of the UAV
            image_path: Path to the image of the UAV
    """
    class UAVState(Enum):
        FREE = 0
        BUSY = 1

    def __init__(self, remain_energy, min_speed, max_speed, buffer_data, recent_position, image_path=None, recent_path=None, target_position=None):
        self.recent_position = recent_position
        self.recent_path = recent_path
        self.index_path = 0
        self.target_position = target_position
        self.status = self.UAVState.FREE
        self.remain_energy = remain_energy
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.direction = Vector(0, 0)
        self.buffer_data = buffer_data
        self.image_path = image_path

    def set_direction(self, vector):
        """
            Set the direction of the UAV
            Args:
                vector: Vector object representing the direction of the UAV
        """
        self.direction = vector.normalize()

    def get_cell_position(self):
        """
            Returns:
                Tuple of cell position (x, y) of the UAV
        """
        x = int(self.recent_position.x // Parameters.cell_size)
        y = int(self.recent_position.y // Parameters.cell_size)
        return (x, y)
    
    def move_a_frame(self):
        """
            Move the UAV a frame
        """
        # self.recent_position.x += self.direction.x * random.uniform(self.min_speed, self.max_speed) / Parameters.FPS
        # self.recent_position.y += self.direction.y * random.uniform(self.min_speed, self.max_speed) / Parameters.FPS
        speed = random.uniform(self.min_speed, self.max_speed)
        if self.recent_path != None:
            if self.index_path < len(self.recent_path):
                target_x, target_y = (self.recent_path[self.index_path][0] * Parameters.cell_size + Parameters.cell_size // 2, self.recent_path[self.index_path][1] * Parameters.cell_size + Parameters.cell_size // 2) 
                dx, dy = target_x - self.recent_position.x, target_y - self.recent_position.y
                self.set_direction(Vector(dx, dy))
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist == 0:  # Nếu UAV gần điểm đích, chuyển sang điểm tiếp theo
                    if self.index_path == len(self.recent_path) - 1:
                        self.status = self.UAVState.FREE
                        self.direction = (0, 0)
                        self.recent_path = None
                    self.index_path += 1
                else:
                    self.recent_position.x += min(abs(speed * self.direction.x / Parameters.FPS), abs(dx)) * get_sign(self.direction.x)
                    self.recent_position.y += min(abs(speed * self.direction.y / Parameters.FPS), abs(dy)) * get_sign(self.direction.y)
    def scan(self, map, cell):
        """
            Scan the map, we assume that scanning is intermediately done by the UAV
            Args:
                map: Map object
        """
        x, y = map.get_cell_position(self.recent_position)
        cx, cy = cell[0], cell[1]
        if (map.state[int(x)][int(y)] == Map.CellState.NOT_SCANNED or map.state[int(x)][int(y)] == Map.CellState.SCANNING):
            map.state[int(x)][int(y)] = Map.CellState.SCANNED

    def transmit_data(self):
        if self.buffer_data > 0:
            print("Transmitting data...")
            self.buffer_data -= 1  # Assuming transmitting data consumes 1 unit of buffer data
        else:
            print("No data to transmit.")

