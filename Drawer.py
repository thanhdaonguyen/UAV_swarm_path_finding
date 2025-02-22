import pygame
from Map import Map
from Parameters import Parameters
import sys

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

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("UAV4Res simulation")
        
        self.window = pygame.display.set_mode((Parameters.map_width * Parameters.cell_size, Parameters.map_height * Parameters.cell_size))
        self.font = pygame.font.SysFont('Arial', 12)
        self.window.fill(Drawer.Color.WHITE)

    def draw_map(self, map):
        """
            Draw the map on the window
            Args:
                map: Map object
        """
        cell_color = {
            Map.CellState.NOT_SCANNED: Drawer.Color.WHITE,
            Map.CellState.SCANNED: Drawer.Color.GREEN,  
            Map.CellState.UNREACHABLE: Drawer.Color.RED,
            Map.CellState.NO_INTEREST: Drawer.Color.GRAY
        }

        for x in range(len(map.state)):
            for y in range(len(map.state[x])):
                text_surface = self.font.render(str(map.state[x][y]), True, (0, 0, 0))
                cell_top_left_point = map.top_left_corner_of_the_cell(x, y)
                pygame.draw.rect(self.window, cell_color[map.state[x][y]], (cell_top_left_point.x, cell_top_left_point.y, Parameters.cell_size, Parameters.cell_size))
                text_rect = text_surface.get_rect(center=(cell_top_left_point.x + Parameters.cell_size // 2, cell_top_left_point.y + Parameters.cell_size // 2))
                self.window.blit(text_surface, text_rect)

    def draw_grid(self):
        """
            Draw the grid on the window
        """
        for x in range(0, Parameters.map_width):
            pygame.draw.line(self.window, (200, 200, 200), (x * Parameters.cell_size, 0), (x * Parameters.cell_size, Parameters.map_height * Parameters.cell_size))
        for y in range(0, Parameters.map_height):
            pygame.draw.line(self.window, (200, 200, 200), (0, y * Parameters.cell_size), (Parameters.map_width * Parameters.cell_size, y * Parameters.cell_size))

    def draw_swarm(self, swarm):
        """
            Draw the swarm on the window
            Args:
                swarm: Swarm object
        """
        pygame.draw.circle(self.window, Drawer.Color.BLUE,(swarm.center.x , swarm.center.y), 5)
        for uav in swarm.uavs:
            if uav.image_path != None:
                uav_image = pygame.image.load(uav.image_path)
                uav_image = pygame.transform.scale(uav_image, (30, 30))
                self.window.blit(uav_image, (uav.recent_position.x, uav.recent_position.y), (0, 0, 30, 30))
            else:
                pygame.draw.circle(self.window, Drawer.Color.BLUE, (uav.recent_position.x, uav.recent_position.y), 5)

    def draw_all(self, map, swarm):
        """
            Draw the map and the swarm on the window
            Args:
                map: Map object
                swarm: Swarm object
        """
        clock = pygame.time.Clock()
        self.window.fill(Drawer.Color.WHITE)
        self.draw_map(map)
        self.draw_swarm(swarm)
        self.draw_grid()
        pygame.display.flip()
        clock.tick(Parameters.FPS)
    
    def kill_window(self):
        pygame.quit()
        sys.exit()