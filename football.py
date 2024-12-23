import pygame
import sys
import random


def play_sound(what_sound):
    if what_sound == "kick":
        kicks = ["kick (1).wav", "kick (2).wav", "kick (3).wav"]
        random_kick = random.choice(kicks)
        random_sound = pygame.mixer.Sound(random_kick)
        random_sound.play()


def game_body():
    # Initialize Pygame
    pygame.init()

    # Constants
    x = 4
    y = 6
    BORDER_SIZE = 70
    GRID_SIZE = 55
    GRID_WIDTH = 2 * x * GRID_SIZE
    GRID_HEIGHT = 2 * y * GRID_SIZE
    WIDTH, HEIGHT = GRID_WIDTH + 2 * BORDER_SIZE, GRID_HEIGHT + 2 * BORDER_SIZE

    FPS = 144

    # Colors
    WHITE = (225, 225, 255)
    PALE_BLUE = (160, 200, 230)  # Pale blue color
    RED = (255, 0, 0)  # Red border
    GREEN = (0, 130, 0)
    DARK_BLUE = (30, 0, 130)  # Dark blue for player path
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 200)

    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Football")
    title_bar_surface = pygame.Surface((WIDTH, 30))
    title_bar_surface.fill(RED)

    # Player starting position
    ball_position = [x * GRID_SIZE + BORDER_SIZE, y * GRID_SIZE + BORDER_SIZE]
    used_paths = []
    used_paths_player1 = []
    used_paths_player2 = []

    # Turn
    first_player = True

    # Directions for Q, W, E, A, D, Z, X, C
    directions = {
        "q": (-GRID_SIZE, -GRID_SIZE),
        "w": (0, -GRID_SIZE),
        "e": (GRID_SIZE, -GRID_SIZE),
        "a": (-GRID_SIZE, 0),
        "d": (GRID_SIZE, 0),
        "z": (-GRID_SIZE, GRID_SIZE),
        "x": (0, GRID_SIZE),
        "c": (GRID_SIZE, GRID_SIZE),
    }
    # Directions for Q, W, E, A, D, Z, X, C
    directions2 = {
        "i": (-GRID_SIZE, -GRID_SIZE),
        "o": (0, -GRID_SIZE),
        "p": (GRID_SIZE, -GRID_SIZE),
        "k": (-GRID_SIZE, 0),
        ";": (GRID_SIZE, 0),
        ",": (-GRID_SIZE, GRID_SIZE),
        ".": (0, GRID_SIZE),
        "/": (GRID_SIZE, GRID_SIZE),
    }

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    # Draw side lines
    for i in range(GRID_SIZE, GRID_HEIGHT - GRID_SIZE, GRID_SIZE):
        startpos = [BORDER_SIZE, i + BORDER_SIZE]
        endpos = [BORDER_SIZE, i + BORDER_SIZE + GRID_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))

        startpos = [GRID_WIDTH + BORDER_SIZE, i + BORDER_SIZE]
        endpos = [GRID_WIDTH + BORDER_SIZE, i + BORDER_SIZE + GRID_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))

    # Draw middle line
    for i in range(BORDER_SIZE, GRID_WIDTH + BORDER_SIZE, GRID_SIZE):
        startpos = [i, BORDER_SIZE + (GRID_HEIGHT) / 2]
        endpos = [i + GRID_SIZE, BORDER_SIZE + GRID_HEIGHT / 2]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))

    # Draw top lines
    for i in range(
        BORDER_SIZE, BORDER_SIZE + int(GRID_WIDTH / 2) - GRID_SIZE, GRID_SIZE
    ):
        startpos = [i, BORDER_SIZE + GRID_SIZE]
        endpos = [i + GRID_SIZE, BORDER_SIZE + GRID_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))
    for i in range(
        int(GRID_WIDTH / 2) + GRID_SIZE + BORDER_SIZE,
        GRID_WIDTH + BORDER_SIZE,
        GRID_SIZE,
    ):
        startpos = [i, BORDER_SIZE + GRID_SIZE]
        endpos = [i + GRID_SIZE, BORDER_SIZE + GRID_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))
    # bottom lines
    for i in range(
        BORDER_SIZE, int(GRID_WIDTH / 2) + BORDER_SIZE - GRID_SIZE, GRID_SIZE
    ):
        startpos = [i, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        endpos = [i + GRID_SIZE, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))
    for i in range(
        int(GRID_WIDTH / 2) + GRID_SIZE + BORDER_SIZE,
        GRID_WIDTH + BORDER_SIZE,
        GRID_SIZE,
    ):
        startpos = [i, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        endpos = [i + GRID_SIZE, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))
    # top goal
    startpos = [int(GRID_WIDTH / 2) + GRID_SIZE + BORDER_SIZE, BORDER_SIZE]
    endpos = [int(GRID_WIDTH / 2) + GRID_SIZE + BORDER_SIZE, BORDER_SIZE + GRID_SIZE]
    pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
    used_paths.append((startpos, endpos))
    startpos = [int(GRID_WIDTH / 2) - GRID_SIZE + BORDER_SIZE, BORDER_SIZE]
    endpos = [int(GRID_WIDTH / 2) - GRID_SIZE + BORDER_SIZE, BORDER_SIZE + GRID_SIZE]
    pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
    used_paths.append((startpos, endpos))
    # bottom goal
    startpos = [
        int(GRID_WIDTH / 2) + GRID_SIZE + BORDER_SIZE,
        GRID_HEIGHT + BORDER_SIZE - GRID_SIZE,
    ]
    endpos = [
        int(GRID_WIDTH / 2) + GRID_SIZE + BORDER_SIZE,
        GRID_HEIGHT + BORDER_SIZE,
    ]
    pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
    used_paths.append((startpos, endpos))
    startpos = [
        int(GRID_WIDTH / 2) - GRID_SIZE + BORDER_SIZE,
        GRID_HEIGHT + BORDER_SIZE - GRID_SIZE,
    ]
    endpos = [
        int(GRID_WIDTH / 2) - GRID_SIZE + BORDER_SIZE,
        GRID_HEIGHT + BORDER_SIZE,
    ]
    pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
    used_paths.append((startpos, endpos))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYUP:
                key = pygame.key.name(event.key).lower()
                if (key in directions and first_player == True) or (
                    key in directions2 and first_player == False
                ):
                    if first_player:
                        new_pos = [
                            ball_position[0] + directions[key][0],
                            ball_position[1] + directions[key][1],
                        ]
                    else:
                        new_pos = [
                            ball_position[0] + directions2[key][0],
                            ball_position[1] + directions2[key][1],
                        ]

                    # Check if the new position is within bounds and not already used
                    if (
                        BORDER_SIZE <= new_pos[0] <= GRID_WIDTH + BORDER_SIZE
                        and BORDER_SIZE <= new_pos[1] <= GRID_HEIGHT + BORDER_SIZE
                        and (ball_position, new_pos) not in used_paths
                        and (new_pos, ball_position) not in used_paths
                    ):
                        #   check if move ended on free spot, if so, switch player
                        change = False
                        if not any(new_pos in path for path in used_paths):
                            change = True
                        # separate paths for playes 1/2
                        if first_player:
                            used_paths_player1.append((ball_position, new_pos))
                        elif not first_player:
                            used_paths_player2.append((ball_position, new_pos))

                        used_paths.append((ball_position, new_pos))
                        play_sound("kick")

                        if change:
                            first_player = not first_player

                        change = False
                        ball_position = new_pos

        # Clear the screen
        screen.fill(WHITE)
        # Draw grid lines
        for x in range(BORDER_SIZE, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, PALE_BLUE, (x, 0), (x, HEIGHT))
        for y in range(BORDER_SIZE, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, PALE_BLUE, (0, y), (WIDTH, y))

        # Draw used paths
        for path in used_paths:
            pygame.draw.line(screen, DARK_BLUE, path[0], path[1], 2)
        for path in used_paths_player1:
            pygame.draw.line(screen, GREEN, path[0], path[1], 3)
        for path in used_paths_player2:
            pygame.draw.line(screen, BLUE, path[0], path[1], 3)

        # Draw player with black circle
        pygame.draw.circle(screen, BLACK, ball_position, GRID_SIZE // 5)

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    # Quit Pygame
    pygame.quit()


game_body()
sys.exit()
