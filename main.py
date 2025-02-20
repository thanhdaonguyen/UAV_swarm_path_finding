import pygame
import sys
from map_setting import AoI, num_of_obstacles_inside, num_of_obstacles_outside
from Map import Map
from UAV import UAV
from Swarm import Swarm
from utils import is_point_in_polygon
from Parameters import Parameters, CellState
import random
from utils import bfs


# Initialize pygame
pygame.init()
map0 = Map(AoI, Parameters.cell_size, Parameters.wind_direction, Parameters.wind_strength, num_of_obstacles_inside=num_of_obstacles_inside,num_of_obstacles_outside = num_of_obstacles_outside, valid_cells=None)
uav=[]
for i in range(Parameters.num_of_uavs):
    uav.append(UAV(random.uniform(0.9,1), 0, random.uniform(30,50), None, 100, 100, "./images/uav.png"))
swarm = Swarm(uav, 605, 445, "V")

# Set up the display
width, height = Parameters.map_width, Parameters.map_height
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("UAV4Res simulation")

# Define colors
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)
gray = (180, 180, 180)


# Fill the background
window.fill(white)


# Mark points inside and outside the polygon
# Initialize font
pygame.font.init()
font = pygame.font.SysFont('Arial', 12)
def draw_map(map):
    for cell in map.cells.values():  # Iterate over the values, which are Cell objects
        if cell.state == CellState.NOT_SCANNED:
            pygame.draw.rect(window, white, (cell.x, cell.y, Parameters.cell_size, Parameters.cell_size))
        elif cell.state == CellState.SCANNED:
            pygame.draw.rect(window, green, (cell.x, cell.y, Parameters.cell_size, Parameters.cell_size))
        elif cell.state == CellState.UNREACHABLE:
            pygame.draw.rect(window, red, (cell.x, cell.y, Parameters.cell_size, Parameters.cell_size))
        elif cell.state == CellState.UNKNOWN:
            pygame.draw.rect(window, blue, (cell.x, cell.y, Parameters.cell_size, Parameters.cell_size))
        elif cell.state == CellState.NO_INTEREST:
            pygame.draw.rect(window, gray, (cell.x, cell.y, Parameters.cell_size, Parameters.cell_size))

        text_surface = font.render(str(cell.value), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(cell.x + Parameters.cell_size // 2, cell.y + Parameters.cell_size // 2))
        window.blit(text_surface, text_rect)


# Draw the grid
def draw_grid():
    step = Parameters.cell_size 
    for x in range(0, width, step):
        pygame.draw.line(window, (200, 200, 200), (x, 0), (x, height))
    for y in range(0, height, step):
        pygame.draw.line(window, (200, 200, 200), (0, y), (width, y))

def draw_swarm(swarm):
    pygame.draw.circle(window, blue,(swarm.x , swarm.y), 5)
    for uav in swarm.uavs:
        if uav.image:
            window.blit(uav.image, (uav.x, uav.y), (0, 0, 30, 30))
        else:
            pygame.draw.circle(window, blue, (uav.x, uav.y), 5)



# Initialize the clock
clock = pygame.time.Clock()

# Wait for the user to close the window
running = True
while running:
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the Swarm
    swarm.calculate_force(map0)  
    swarm.move()
    swarm.scan(map0)

    # Redraw the screen
    window.fill(white)
    draw_map(map0)
    draw_grid()
    draw_swarm(swarm)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
