import pygame
import sys
import random
import math


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
    BORDER_SIZE = 150
    GRID_SIZE = 55

    GRID_WIDTH = 2 * x * GRID_SIZE
    GRID_HEIGHT = 2 * y * GRID_SIZE
    WIDTH, HEIGHT = GRID_WIDTH + 2 * BORDER_SIZE, GRID_HEIGHT + 2 * BORDER_SIZE

    FPS = 144

    WHITE = (225, 225, 255)
    PALE_BLUE = (160, 200, 230)
    RED = (255, 0, 0)
    GREEN = (0, 130, 0)
    DARK_BLUE = (30, 0, 130)
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 200)
    DARK_GREY = (100, 100, 100)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Football")

    ball_position = [x * GRID_SIZE + BORDER_SIZE, y * GRID_SIZE + BORDER_SIZE]
    used_paths = []
    used_paths_player1 = []  # to color only
    used_paths_player2 = []  # to color only
    invisible_paths = []  # eraser (visual only)

    player_font = pygame.font.SysFont("Georgia", 36)
    victory_font = pygame.font.SysFont("Cambria", 72)
    info_font = pygame.font.SysFont("Ariel", 20)

    img = pygame.image.load("ball.png")
    img = pygame.transform.scale(img, (GRID_SIZE * 0.5, GRID_SIZE * 0.5))
    first_player = True  # Turn
    first_player_won = False
    second_player_won = False

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
    # Directions for I, O, P, K, ";", ",", ".", "/"
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

    def win_condition(position):
        if position[1] == BORDER_SIZE and (
            position[0] == int(GRID_WIDTH / 2) + BORDER_SIZE
            or position[0] == int(GRID_WIDTH / 2) + BORDER_SIZE - GRID_SIZE
            or position[0] == int(GRID_WIDTH / 2) + BORDER_SIZE + GRID_SIZE
        ):
            return "first"
        elif position[1] == BORDER_SIZE + GRID_HEIGHT and (
            position[0] == int(GRID_WIDTH / 2) + BORDER_SIZE
            or position[0] == int(GRID_WIDTH / 2) + BORDER_SIZE - GRID_SIZE
            or position[0] == int(GRID_WIDTH / 2) + BORDER_SIZE + GRID_SIZE
        ):
            return "second"
        else:
            return "in progress"

    def cant_move(new_temp_pos):
        if (
            BORDER_SIZE <= new_temp_pos[0] <= GRID_WIDTH + BORDER_SIZE
            and BORDER_SIZE <= new_temp_pos[1] <= GRID_HEIGHT + BORDER_SIZE
            and (ball_position, new_temp_pos) not in used_paths
            and (new_temp_pos, ball_position) not in used_paths
        ):
            return False
        return True

    def blocked():
        directions_available = 8
        new_pos = [ball_position[0] - GRID_SIZE, ball_position[1] - GRID_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_position[0], ball_position[1] - GRID_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_position[0] + GRID_SIZE, ball_position[1] - GRID_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_position[0] - GRID_SIZE, ball_position[1]]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_position[0] + GRID_SIZE, ball_position[1]]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_position[0] - GRID_SIZE, ball_position[1] + GRID_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_position[0], ball_position[1] + GRID_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_position[0] + GRID_SIZE, ball_position[1] + GRID_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        return directions_available

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    # used_paths bloks moves and provides extra move
    # invisible_paths hides used_paths

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

    # Draw top lines, including all blocked outside
    for i in range(BORDER_SIZE, GRID_WIDTH + BORDER_SIZE, GRID_SIZE):
        startpos = [i, BORDER_SIZE]
        endpos = [i + GRID_SIZE, BORDER_SIZE]
        used_paths.append((startpos, endpos))
        invisible_paths.append((startpos, endpos))
    for i in range(
        BORDER_SIZE, BORDER_SIZE + int(GRID_WIDTH / 2) - GRID_SIZE, GRID_SIZE
    ):
        startpos = [i, BORDER_SIZE + GRID_SIZE]
        endpos = [i + GRID_SIZE, BORDER_SIZE + GRID_SIZE]
        endpos2 = [i + GRID_SIZE, BORDER_SIZE]
        endpos3 = [i, BORDER_SIZE]
        startpos2 = [i + GRID_SIZE, BORDER_SIZE + GRID_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))
        used_paths.append((startpos, endpos2))
        used_paths.append((startpos, endpos3))
        used_paths.append((startpos2, endpos3))
        invisible_paths.append((startpos, endpos2))
        invisible_paths.append((startpos, endpos3))
        invisible_paths.append((startpos2, endpos3))

    for i in range(
        int(GRID_WIDTH / 2) + GRID_SIZE + BORDER_SIZE,
        GRID_WIDTH + BORDER_SIZE,
        GRID_SIZE,
    ):
        startpos = [i, BORDER_SIZE + GRID_SIZE]
        endpos = [i + GRID_SIZE, BORDER_SIZE + GRID_SIZE]
        endpos2 = [i + GRID_SIZE, BORDER_SIZE]
        startpos2 = [i + GRID_SIZE, BORDER_SIZE + GRID_SIZE]
        endpos3 = [i, BORDER_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))
        used_paths.append((startpos, endpos2))
        used_paths.append((startpos2, endpos2))
        used_paths.append((startpos2, endpos3))
        invisible_paths.append((startpos, endpos2))
        invisible_paths.append((startpos2, endpos2))
        invisible_paths.append((startpos2, endpos3))

    # bottom lines, including all invisible blocked outs
    for i in range(BORDER_SIZE, GRID_WIDTH + BORDER_SIZE, GRID_SIZE):
        startpos = [i, GRID_HEIGHT + BORDER_SIZE]
        endpos = [i + GRID_SIZE, GRID_HEIGHT + BORDER_SIZE]
        used_paths.append((startpos, endpos))
        invisible_paths.append((startpos, endpos))
    for i in range(
        BORDER_SIZE, int(GRID_WIDTH / 2) + BORDER_SIZE - GRID_SIZE, GRID_SIZE
    ):
        startpos = [i, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        endpos = [i + GRID_SIZE, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        endpos2 = [i + GRID_SIZE, GRID_HEIGHT + BORDER_SIZE]
        endpos3 = [i, GRID_HEIGHT + BORDER_SIZE]
        startpos2 = [i + GRID_SIZE, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))
        used_paths.append((startpos, endpos2))
        used_paths.append((startpos, endpos3))
        used_paths.append((startpos2, endpos3))
        invisible_paths.append((startpos, endpos2))
        invisible_paths.append((startpos, endpos3))
        invisible_paths.append((startpos2, endpos3))

    for i in range(
        int(GRID_WIDTH / 2) + GRID_SIZE + BORDER_SIZE,
        GRID_WIDTH + BORDER_SIZE,
        GRID_SIZE,
    ):
        startpos = [i, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        endpos = [i + GRID_SIZE, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        endpos2 = [i + GRID_SIZE, GRID_HEIGHT + BORDER_SIZE]
        startpos2 = [i + GRID_SIZE, GRID_HEIGHT + BORDER_SIZE - GRID_SIZE]
        endpos3 = [i, GRID_HEIGHT + BORDER_SIZE]
        pygame.draw.line(screen, DARK_BLUE, startpos, endpos, 3)
        used_paths.append((startpos, endpos))
        used_paths.append((startpos, endpos2))
        used_paths.append((startpos2, endpos2))
        used_paths.append((startpos2, endpos3))
        invisible_paths.append((startpos, endpos2))
        invisible_paths.append((startpos2, endpos2))
        invisible_paths.append((startpos2, endpos3))

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

    def findbestpath():
        alldirections = [
            (-GRID_SIZE, -GRID_SIZE),
            (0, -GRID_SIZE),
            (GRID_SIZE, -GRID_SIZE),
            (GRID_SIZE, 0),
            (GRID_SIZE, GRID_SIZE),
            (0, GRID_SIZE),
            (-GRID_SIZE, GRID_SIZE),
            (-GRID_SIZE, 0),
        ]

    global restarting_loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                restarting_loop = False
                running = False
            elif event.type == pygame.KEYUP:
                key = pygame.key.name(event.key).lower()
                if event.key == pygame.K_ESCAPE:
                    restarting_loop = False
                    running = False
                if event.key == pygame.K_F3:
                    findbestpath()
                if event.key == pygame.K_F5:
                    running = False
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
                        # separate paths for playes 1/2 for recoloring only
                        if first_player:
                            used_paths_player1.append((ball_position, new_pos))
                        elif not first_player:
                            used_paths_player2.append((ball_position, new_pos))

                        used_paths.append((ball_position, new_pos))
                        play_sound("kick")
                        if win_condition(new_pos) == "first":
                            first_player_won = True
                        elif win_condition(new_pos) == "second":
                            second_player_won = True

                        if change:
                            first_player = not first_player

                        ball_position = new_pos
                        if blocked() == 0:
                            if first_player:
                                second_player_won = True
                            else:
                                first_player_won = True

                        change = False

        if not running:
            pygame.quit()
            return

        # Clear the screen
        screen.fill(WHITE)
        # Draw grid lines
        for x in range(BORDER_SIZE - 5 * GRID_SIZE, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, PALE_BLUE, (x, 0), (x, HEIGHT))
        for y in range(BORDER_SIZE - 5 * GRID_SIZE, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, PALE_BLUE, (0, y), (WIDTH, y))

        # Draw used paths
        for path in used_paths:  # all blocked, lines/goals/moves
            pygame.draw.line(screen, DARK_BLUE, path[0], path[1], 2)
        for path in used_paths_player1:
            pygame.draw.line(screen, GREEN, path[0], path[1], 3)
        for path in used_paths_player2:
            pygame.draw.line(screen, BLUE, path[0], path[1], 3)
        for path in invisible_paths:  # paint over with white
            pygame.draw.line(screen, WHITE, path[0], path[1], 3)
        # Draw ball with black circle or image
        # pygame.draw.circle(screen, DARK_GREY, ball_position, GRID_SIZE // 5)

        rect = img.get_rect()
        rect.center = ball_position
        screen.blit(img, rect)

        player_font.bold = True
        player_font.italic = True
        victory_font.bold = True
        p1_text = player_font.render("Player 1", 36, GREEN)
        p2_text = player_font.render("Player 2", 36, BLUE)
        info_text = info_font.render(f"ESC to quit", 20, PALE_BLUE)
        screen.blit(
            info_text,
            (BORDER_SIZE + 5, HEIGHT - BORDER_SIZE - GRID_SIZE + GRID_SIZE // 4),
        )
        info_text = info_font.render(f"F5 to restart", 20, PALE_BLUE)
        screen.blit(
            info_text,
            (BORDER_SIZE + 5, HEIGHT - BORDER_SIZE - GRID_SIZE + GRID_SIZE // 4 + 20),
        )

        if first_player_won:
            victory_text = victory_font.render("Player 1 WON!", 36, RED)
            screen.blit(
                victory_text,
                (
                    WIDTH // 2 - victory_text.get_width() // 2,
                    HEIGHT // 2 - victory_text.get_height(),
                ),
            )
        if second_player_won:
            victory_text = victory_font.render("Player 2 WON!", 36, RED)
            screen.blit(
                victory_text,
                (
                    WIDTH // 2 - victory_text.get_width() // 2,
                    HEIGHT // 2 - victory_text.get_height(),
                ),
            )

        screen.blit(
            p1_text,
            (WIDTH // 2 + GRID_SIZE * 1.5, HEIGHT - BORDER_SIZE - GRID_SIZE * 0.8),
        )
        screen.blit(
            p2_text,
            (
                WIDTH // 2 - GRID_SIZE * 1.5 - p2_text.get_width(),
                BORDER_SIZE + GRID_SIZE - GRID_SIZE * 0.8,
            ),
        )
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


global restarting_loop
restarting_loop = True
while restarting_loop:
    print("start")
    game_body()
    print(restarting_loop)

sys.exit()
