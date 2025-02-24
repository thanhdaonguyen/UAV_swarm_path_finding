from utils import Vector
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
        return tuple[self.recent_position.x // Parameters.cell_size, self.recent_position.y // Parameters.cell_size]

    def move_a_frame(self):
        """
            Move the UAV a frame
        """
        self.recent_position.x += self.direction.x * random.uniform(self.min_speed, self.max_speed) / Parameters.FPS
        self.recent_position.y += self.direction.y * random.uniform(self.min_speed, self.max_speed) / Parameters.FPS

    def scanf(self, map):
        """
            Scan the map, we assume that scanning is intermediately done by the UAV
            Args:
                map: Map object
        """
        # map.state[map.get_cell_position(self.recent_position)] = Map.CellState.SCANNED
        cell_x, cell_y = map.get_cell_position(self.recent_position)  # Unpack the tuple into separate indices
        map.state[int(cell_x)][int(cell_y)] = Map.CellState.SCANNED

    def transmit_data(self):
        if self.buffer_data > 0:
            print("Transmitting data...")
            self.buffer_data -= 1  # Assuming transmitting data consumes 1 unit of buffer data
        else:
            print("No data to transmit.")

