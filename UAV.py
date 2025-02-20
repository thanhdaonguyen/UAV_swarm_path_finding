
import pygame
from Map import CellState

class UAV:
    def __init__(self, remain_energy, min_speed, max_speed, buffer_data, pos_X=100, pos_Y=100, image_path=None):
        self.x = pos_X
        self.y = pos_Y
        self.remain_energy = remain_energy
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.buffer_data = buffer_data
        self.force_vector = [0, 0]
        if image_path:
            self.load_image(image_path)


    def load_image(self, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (30, 30))

    def scan(self, map):
        for cell in map.cells.values():
            if cell.state == CellState.NOT_SCANNED and cell.state != CellState.UNREACHABLE:
                if (self.x - cell.x) ** 2 + (self.y - cell.y) ** 2 < 100:
                    cell.state = CellState.SCANNED
                    cell.update_value(0)

    def calculate_force(self, centroid_x, centroid_y, uavs):
        force_x = centroid_x - self.x
        force_y = centroid_y - self.y

        for uav in uavs:
            if uav != self:
                distance = ((uav.x - self.x) ** 2 + (uav.y - self.y) ** 2) ** 0.5
                if distance < 50:
                    force_x += self.x - uav.x
                    force_y += self.y - uav.y

        #normalize the force vector
        force_magnitude = (force_x ** 2 + force_y ** 2) ** 0.5
        if force_magnitude > 0:
            force_x /= force_magnitude
            force_y /= force_magnitude
        self.force_vector = [force_x, force_y]

    def move(self, centroid_x, centroid_y, uavs):
        self.calculate_force(centroid_x, centroid_y, uavs)
        self.x += self.force_vector[0]
        self.y += self.force_vector[1]


    def transmit_data(self):
        if self.buffer_data > 0:
            print("Transmitting data...")
            self.buffer_data -= 1  # Assuming transmitting data consumes 1 unit of buffer data
        else:
            print("No data to transmit.")

