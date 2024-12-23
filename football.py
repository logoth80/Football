import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
BORDER_SIZE=20
GRID_SIZE = 40
GRID_WIDTH = 10 * GRID_SIZE
GRID_HEIGHT = 20 * GRID_SIZE
WIDTH, HEIGHT = GRID_WIDTH+2*BORDER_SIZE, GRID_HEIGHT+2*BORDER_SIZE

FPS = 30

# Colors
WHITE = (235, 235, 255)

PALE_BLUE = (173, 216, 230)  # Pale blue color
RED = (255, 0, 0)  # Red border
DARK_BLUE = (0, 0, 100)  # Dark blue for player path
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Game")

# Player starting position
player_pos = [5* GRID_SIZE+BORDER_SIZE, 10 * GRID_SIZE+BORDER_SIZE]
used_paths = []

# Directions for Q, W, E, A, D, Z, X, C
directions = {
    'q': (-GRID_SIZE, -GRID_SIZE),
    'w': (0, -GRID_SIZE),
    'e': (GRID_SIZE, -GRID_SIZE),
    'a': (-GRID_SIZE, 0),
    'd': (GRID_SIZE, 0),
    'z': (-GRID_SIZE, GRID_SIZE),
    'x': (0, GRID_SIZE),
    'c': (GRID_SIZE, GRID_SIZE)
}

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP:
            key = pygame.key.name(event.key).lower()
            if key in directions:
                new_pos = [player_pos[0] + directions[key][0], player_pos[1] + directions[key][1]]
                
                # Check if the new position is within bounds and not already used
                if BORDER_SIZE <= new_pos[0] <= GRID_WIDTH + BORDER_SIZE and \
                    BORDER_SIZE <= new_pos[1] <= GRID_HEIGHT + BORDER_SIZE and \
                    (player_pos, new_pos) not in used_paths and (new_pos, player_pos) not in used_paths:

                    used_paths.append((player_pos, new_pos))
                    player_pos = new_pos

    # Clear the screen
    screen.fill(WHITE)

    # Draw grid lines with PALE_BLUE
    for x in range(BORDER_SIZE, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, PALE_BLUE, (x, 0), (x, HEIGHT))
    for y in range(BORDER_SIZE, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, PALE_BLUE, (0, y), (WIDTH, y))


    # Draw used paths with dark blue
    for path in used_paths:
        pygame.draw.line(screen, DARK_BLUE, path[0], path[1])

    # Draw player with black circle
    pygame.draw.circle(screen, BLACK, player_pos, GRID_SIZE // 2)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()
