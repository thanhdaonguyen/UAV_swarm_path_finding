from UAV import UAV
from utils import Point, Vector
from Parameters import Parameters
import random
import Map
class Swarm:
    """
        Swarm class to represent a swarm of UAVs
        Attributes:
            uavs: List of UAV objects
            center: Point object representing the center of the swarm
            formation: String representing the formation of the swarm
    """
    def __init__(self, uavs, center, formation):
        self.uavs = uavs
        self.center = center
        self.formation = formation
        self.force_vector = [0, 0]
    def set_center(self, point):
        """
            Set the center of the swarm
            Args:
                point: Point object representing the new center of the swarm
        """
        self.center = point
    
    def get_center_cell_position(self):
        """
            Returns:
                Tuple of cell position (x, y) of the center of the swarm
        """
        return tuple([self.center.x // Parameters.cell_size, self.center.y // Parameters.cell_size])
    def calculate_force(self, map):
        # Placeholder for force calculation logic
        force_vector = [0.5, 0.5]
        for cell in map.cells.values():
            if cell.state == Map.CellState.NOT_SCANNED:
                distance = ((cell.x - self.x) ** 2 + (cell.y - self.y) ** 2) ** 0.5
                force_x = (cell.x - self.x) / (distance+1)
                force_y = (cell.y - self.y) / (distance+1)
                force_vector[0] += force_x * cell.value
                force_vector[1] += force_y * cell.value
        # Normalize the force vector
        print(self.force_vector)
        force_x = force_vector[0] / (force_vector[0] ** 2 + force_vector[1] ** 2) ** 0.5
        force_y = force_vector[1] / (force_vector[0] ** 2 + force_vector[1] ** 2) ** 0.5
        self.force_vector = (force_x, force_y)

    def move_a_frame(self):
        """
            Move the swarm a frame
        """
        for uav in self.uavs:
            uav.move_a_frame()

    def scan(self, map):
        """
            Scan the map
            Args:
                map: Map object
        """
        for uav in self.uavs:
            uav.scan(map)

    def __repr__(self):
        return f"Swarm(posX={self.center.x}, posY={self.center.y}, formation={self.formation}, uavs={self.uavs})"