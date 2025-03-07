import pygame
from Map import Map, Point
import sys
from input import *
import os
class Drawer:
    """
        Class responsible for drawing the simulation
    """
    class Color:
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255)
        YELLOW = (255, 255, 0)
        CYAN = (0, 255, 255)
        MAGENTA = (255, 0, 255)
        GRAY = (180, 180, 180)

    def __init__(self, mode):
        pygame.init()
        pygame.font.init()

        if mode == "tsunami":
            pygame.display.set_caption("Tsunami simulation")
            os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"  # Change "100,100" to your desired position
        
        elif mode == "UAV4Res":
            pygame.display.set_caption("UAV4Res simulation")
            os.environ['SDL_VIDEO_WINDOW_POS'] = "900,100"  # Change "800,100" to your desired position
        else :
            pygame.display.set_caption("Random UAV simulation")
            os.environ['SDL_VIDEO_WINDOW_POS'] = "100,600"
        self.window = pygame.display.set_mode((map_width * cell_size, map_height * cell_size))
        self.font = pygame.font.SysFont('Arial', 12)
        self.window.fill(Drawer.Color.WHITE)
        self.clock = pygame.time.Clock()

    def draw_map(self, map):
        """
            Draw the map on the window
            Args:
                map: Map object
        """
        cell_color = {
            Map.CellState.SCANNING: Drawer.Color.YELLOW,
            Map.CellState.NOT_SCANNED: Drawer.Color.WHITE,
            Map.CellState.SCANNED: Drawer.Color.GREEN,  
            Map.CellState.UNREACHABLE: Drawer.Color.RED,
            Map.CellState.NO_INTEREST: Drawer.Color.GRAY
        }

        for x in range(len(map.state)):
            for y in range(len(map.state[x])):
                text_surface = self.font.render(str(map.priority[x][y]), True, (0, 0, 0))
                cell_top_left_point = map.top_left_corner_of_the_cell(x, y)
                pygame.draw.rect(self.window, cell_color[map.state[x][y]], (cell_top_left_point.x, cell_top_left_point.y, cell_size, cell_size))
                text_rect = text_surface.get_rect(center=(cell_top_left_point.x + cell_size // 2, cell_top_left_point.y + cell_size // 2))
                self.window.blit(text_surface, text_rect)

    def draw_grid(self):
        """
            Draw the grid on the window
        """
        for x in range(0, map_width):
            pygame.draw.line(self.window, (200, 200, 200), (x * cell_size, 0), (x * cell_size, map_height * cell_size))
        for y in range(0, map_height):
            pygame.draw.line(self.window, (200, 200, 200), (0, y * cell_size), (map_width * cell_size, y * cell_size))

    def draw_swarm(self, swarm):
        """
            Draw the swarm on the window
            Args:
                swarm: Swarm object
        """
        pygame.draw.circle(self.window, Drawer.Color.BLUE,(swarm.center.x,  swarm.center.y), 5)
        for uav in swarm.uavs:
            if uav.image_path != None:
                scaled_width = cell_size
                scaled_height = cell_size
                uav_image = pygame.image.load(uav.image_path)
                uav_image = pygame.transform.scale(uav_image, (scaled_width, scaled_height))
                self.window.blit(uav_image, (uav.recent_position.x - scaled_width / 2, uav.recent_position.y - scaled_height / 2), (0, 0, 30, 30))
            else:
                pygame.draw.circle(self.window, Drawer.Color.BLUE, (uav.recent_position.x, uav.recent_position.y), 5)

    def draw_circles(self, centers):
        for center in centers:
            pygame.draw.circle(self.window, Drawer.Color.BLUE, center, int(cell_radius*cell_size), 1)

    def draw_cluster_cells(self):
        # print(Map.cluster_cells)
        for x, y in Map.cluster_cells:
            pygame.draw.circle(self.window, Drawer.Color.MAGENTA, (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2), 3)

    def draw_wavefront_map(self, wavefront_map):
        """
            Draw the wavefront map on the window
            Args:
                wavefront_map: 2D array representing the wavefront map
        """
        max_value = max([max(row) for row in wavefront_map])
        for x in range(len(wavefront_map)):
            for y in range(len(wavefront_map[x])):
                if wavefront_map[x][y] > 0:
                    pygame.draw.circle(self.window, Drawer.Color.CYAN, (x * cell_size + cell_size // 4, y * cell_size + cell_size // 4), 10 * int(wavefront_map[x][y]) / max_value)
                

    def draw_all(self, map, swarm, cir_centers, wavefront_map=None):
        """
            Draw the map and the swarm on the window
            Args:
                map: Map object
                swarm: Swarm object
        """
        self.window.fill(Drawer.Color.WHITE)
        self.draw_map(map)
        self.draw_swarm(swarm)
        circle_centers = []
        for i in range(len(cir_centers)):
            circle_centers.append((cir_centers[i][0], cir_centers[i][1]))
        self.draw_circles(circle_centers)
        self.draw_cluster_cells()
        # self.draw_wavefront_map(wavefront_map)
        self.draw_grid()
        pygame.display.flip()

    
    def kill_window(self):
        pygame.quit()
        sys.exit()