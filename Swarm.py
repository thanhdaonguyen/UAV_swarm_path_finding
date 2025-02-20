
from UAV import UAV
from Map import CellState
import random

class Swarm:
    def __init__(self, uavs, posX, posY, formation):
        self.uavs = uavs  # List of UAV objects
        self.x = posX
        self.y = posY
        self.formation = formation
        self.force_vector = [0, 0]

    def move(self):
        self.x += self.force_vector[0]
        self.y += self.force_vector[1]
        for uav in self.uavs:
            uav.move(self.x, self.y, self.uavs)
        

    def calculate_force(self, map):
        # Placeholder for force calculation logic
        force_vector = [0, 0]
        for cell in map.cells.values():
            if cell.state == CellState.NOT_SCANNED and cell.state != CellState.UNREACHABLE:
                distance = ((cell.x - self.x) ** 2 + (cell.y - self.y) ** 2) ** 0.5
                force_x = (cell.x - self.x) / distance
                force_y = (cell.y - self.y) / distance
                force_vector[0] += force_x * cell.value
                force_vector[1] += force_y * cell.value
        # Normalize the force vector
        # print(self.force_vector)
        force_x = force_vector[0] / (force_vector[0] ** 2 + force_vector[1] ** 2) ** 0.5
        force_y = force_vector[1] / (force_vector[0] ** 2 + force_vector[1] ** 2) ** 0.5
        self.force_vector = (force_x, force_y)

        

    def scan(self, map):
        for uav in self.uavs:
            uav.scan(map)

    def __repr__(self):
        return f"Swarm(posX={self.posX}, posY={self.posY}, formation={self.formation}, uavs={self.uavs})"