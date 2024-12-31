import pygame
import sys
import random
import time

player2_text = "Player 2"
versus_ai = False


def calculate_best_move(
    ball_position,
    directions,
    used_paths,
    BORDER_SIZE,
    GRID_WIDTH,
    GRID_HEIGHT,
    GRID_SIZE,
    opponent_directions,
):
    def is_valid_move(current_position, new_pos, path):
        # Check if a move is valid.
        return (
            BORDER_SIZE <= new_pos[0] <= GRID_WIDTH + BORDER_SIZE
            and BORDER_SIZE <= new_pos[1] <= GRID_HEIGHT + 2 * BORDER_SIZE
            and (current_position, new_pos) not in used_paths
            and (new_pos, current_position) not in used_paths
            and (current_position, new_pos) not in path
            and (new_pos, current_position) not in path
        )

    def bounce(new_pos):
        return any(new_pos in path for path in used_paths)

    def cant_move(new_temp_pos, path):  # can't move in that direction
        if (
            BORDER_SIZE <= new_temp_pos[0] <= GRID_WIDTH + BORDER_SIZE
            and BORDER_SIZE <= new_temp_pos[1] <= GRID_HEIGHT + BORDER_SIZE
            and (ball_position, new_temp_pos) not in used_paths
            and (new_temp_pos, ball_position) not in used_paths
            and (ball_position, new_temp_pos) not in path
            and (new_temp_pos, ball_position) not in path
        ):
            return False
        return True

    def blocked(
        test_pos, path
    ):  # returns free paths (0=none) from point, blocking way in with path
        directions_available = 8
        new_pos = [test_pos[0] - GRID_SIZE, test_pos[1] - GRID_SIZE]
        if cant_move(new_pos, path):
            directions_available = directions_available - 1
        new_pos = [test_pos[0], test_pos[1] - GRID_SIZE]
        if cant_move(new_pos, path):
            directions_available = directions_available - 1
        new_pos = [test_pos[0] + GRID_SIZE, test_pos[1] - GRID_SIZE]
        if cant_move(new_pos, path):
            directions_available = directions_available - 1
        new_pos = [test_pos[0] - GRID_SIZE, test_pos[1]]
        if cant_move(new_pos, path):
            directions_available = directions_available - 1
        new_pos = [test_pos[0] + GRID_SIZE, test_pos[1]]
        if cant_move(new_pos, path):
            directions_available = directions_available - 1
        new_pos = [test_pos[0] - GRID_SIZE, test_pos[1] + GRID_SIZE]
        if cant_move(new_pos, path):
            directions_available = directions_available - 1
        new_pos = [test_pos[0], test_pos[1] + GRID_SIZE]
        if cant_move(new_pos, path):
            directions_available = directions_available - 1
        new_pos = [test_pos[0] + GRID_SIZE, test_pos[1] + GRID_SIZE]
        if cant_move(new_pos, path):
            directions_available = directions_available - 1
        return directions_available

    def distance_to_goal(position):  # south goal
        distancey = abs(position[1] - (BORDER_SIZE + GRID_HEIGHT))
        distancex = abs(position[0] - (GRID_WIDTH // 2 + BORDER_SIZE))
        return distancex * distancex + distancey * distancey

    def explore_paths(
        current_position, tested_path, best_move, best_score, time_started
    ):
        # Recursively explore all possible paths.
        if time.time() > time_started + 3:
            return best_move, best_score
        for direction_key, direction in directions.items():
            new_pos = [
                current_position[0] + direction[0],
                current_position[1] + direction[1],
            ]

            if is_valid_move(current_position, new_pos, tested_path):
                tested_path.append((current_position, new_pos))

                if bounce(new_pos) and blocked(new_pos, tested_path) > 0:
                    # Recurse deeper for further moves
                    best_move, best_score = explore_paths(
                        new_pos, tested_path, best_move, best_score, time_started
                    )
                elif bounce(new_pos):  # blocked
                    current_score = float("inf")
                    tested_path.pop()
                else:
                    # finished on empty spod, end of that path
                    current_score = distance_to_goal(new_pos)
                    if current_score < best_score:
                        best_score = current_score
                        best_move = tested_path[:]
                    elif current_score == best_score:
                        if random.random() > 0.5:
                            best_score = current_score
                            best_move = tested_path[:]
                # Backtrack
                tested_path.pop()
        return best_move, best_score

    best_move = []
    best_score = float("inf")  # Lower scores are better
    tested_path = []

    # Start the recursive exploration
    time_started = time.time()  # to check max time
    best_move, best_score = explore_paths(
        ball_position, tested_path, best_move, best_score, time_started
    )
    waited = time.time() - time_started
    if waited < 1.5:  # minimum delay for AI move
        pygame.time.delay(1500 - int(waited * 10000))
    return best_move


def play_sound(what_sound):
    if what_sound == "kick":
        kicks = ["kick (1).wav", "kick (2).wav", "kick (3).wav"]
        random_kick = random.choice(kicks)
        random_sound = pygame.mixer.Sound(random_kick)
        random_sound.play()


def game_body():
    pygame.init()
    x = 4
    y = 6
    BORDER_SIZE = 150
    GRID_SIZE = 55

    GRID_WIDTH = 2 * x * GRID_SIZE
    GRID_HEIGHT = 2 * y * GRID_SIZE
    WIDTH, HEIGHT = GRID_WIDTH + 2 * BORDER_SIZE, GRID_HEIGHT + 2 * BORDER_SIZE
    half_h = HEIGHT / 2
    half_w = WIDTH / 2
    FPS = 144

    WHITE = (225, 225, 255)
    PALE_BLUE = (160, 200, 230)
    RED = (255, 0, 0)
    GREEN = (0, 130, 0)
    DARK_BLUE = (30, 0, 130)
    BLUE = (0, 0, 200)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Football")

    ball_position = [x * GRID_SIZE + BORDER_SIZE, y * GRID_SIZE + BORDER_SIZE]
    used_paths = []
    used_paths_player1 = []  # to color only
    used_paths_player2 = []
    invisible_paths = []  # eraser (visual only)

    player_font = pygame.font.SysFont("Georgia", 36)
    v_font = pygame.font.SysFont("Cambria", 72)
    info_font = pygame.font.SysFont("Ariel", 20)

    img = pygame.image.load("ball.png")
    img = pygame.transform.scale(img, (GRID_SIZE * 0.5, GRID_SIZE * 0.5))
    first_player = True  # Turn
    fpwon = False
    spwon = False

    # Player 1
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
    # Player 2
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

    def blocked():  # not for AI
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

    def cpu_move(best_move):
        for one_step in best_move:
            # print(one_step)
            used_paths.append(one_step)
            used_paths_player2.append(one_step)
            pygame.draw.line(screen, DARK_BLUE, one_step[0], one_step[1], 3)
            ball_position = one_step[1]
            rect = img.get_rect()
            rect.center = ball_position
            screen.blit(img, rect)
            play_sound("kick")
            pygame.time.wait(50)
            pygame.display.flip()
            pygame.time.wait(200)
        return ball_position

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    # used_paths bloks moves and provides extra move
    # invisible_paths hides used_paths outside lines

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

    global restarting_loop  # so game doesn't just quit
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
                if event.key == pygame.K_F3:  # ai / player2
                    global versus_ai
                    versus_ai = not versus_ai
                    global player2_text
                    if player2_text == "Player 2":
                        player2_text = "CPU"
                    else:
                        player2_text = "Player 2"

                if event.key == pygame.K_F5:
                    running = False
                if (key in directions and first_player == True and not spwon) or (
                    key in directions2 and first_player == False and not fpwon
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
                            fpwon = True
                        elif win_condition(new_pos) == "second":
                            spwon = True

                        if change:
                            first_player = not first_player

                        ball_position = new_pos
                        if blocked() == 0:
                            if first_player:
                                spwon = True
                            else:
                                fpwon = True

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
        for (
            path
        ) in used_paths:  # all blocked and bounce enabling, all lines/goals/moves
            pygame.draw.line(screen, DARK_BLUE, path[0], path[1], 2)
        for path in used_paths_player1:
            pygame.draw.line(screen, GREEN, path[0], path[1], 3)
        for path in used_paths_player2:
            pygame.draw.line(screen, BLUE, path[0], path[1], 3)
        for path in invisible_paths:  # paint over with white
            pygame.draw.line(screen, WHITE, path[0], path[1], 3)
        # Draw ball with image
        rect = img.get_rect()
        rect.center = ball_position
        screen.blit(img, rect)

        player_font.bold = True
        player_font.italic = True
        v_font.bold = True
        p1_text = player_font.render("Player 1", 36, GREEN)
        p2_text = player_font.render(player2_text, 36, BLUE)

        if player2_text == "Player 2":
            info_text = info_font.render(f"I  O  P", 20, DARK_BLUE)
            screen.blit(
                info_text,
                (
                    WIDTH - 2 * BORDER_SIZE + 5,
                    BORDER_SIZE - 2 * GRID_SIZE + GRID_SIZE // 4 + 95,
                ),
            )
            info_text = info_font.render(f"K      ;  -  to move", 20, DARK_BLUE)
            screen.blit(
                info_text,
                (
                    WIDTH - 2 * BORDER_SIZE + 5,
                    BORDER_SIZE - 2 * GRID_SIZE + GRID_SIZE // 4 + 113,
                ),
            )
            info_text = info_font.render(f",   .   /", 20, DARK_BLUE)
            screen.blit(
                info_text,
                (
                    WIDTH - 2 * BORDER_SIZE + 5,
                    BORDER_SIZE - 2 * GRID_SIZE + GRID_SIZE // 4 + 131,
                ),
            )

        info_text = info_font.render(f"ESC to quit", 20, DARK_BLUE)
        screen.blit(
            info_text,
            (BORDER_SIZE + 5, HEIGHT - BORDER_SIZE - GRID_SIZE + GRID_SIZE // 4),
        )

        info_text = info_font.render(f"F5 to restart", 20, DARK_BLUE)
        screen.blit(
            info_text,
            (BORDER_SIZE + 5, HEIGHT - BORDER_SIZE - GRID_SIZE + GRID_SIZE // 4 + 24),
        )

        info_text = info_font.render(f"F3 to switch to versus CPU", 20, DARK_BLUE)
        screen.blit(
            info_text,
            (BORDER_SIZE + 5, HEIGHT - BORDER_SIZE - GRID_SIZE + GRID_SIZE // 4 + 48),
        )
        info_text = info_font.render(f"Q W E", 20, DARK_BLUE)
        screen.blit(
            info_text,
            (BORDER_SIZE + 5, HEIGHT - BORDER_SIZE - GRID_SIZE + GRID_SIZE // 4 + 72),
        )
        info_text = info_font.render(f"A     D  -  to move", 20, DARK_BLUE)
        screen.blit(
            info_text,
            (BORDER_SIZE + 5, HEIGHT - BORDER_SIZE - GRID_SIZE + GRID_SIZE // 4 + 92),
        )
        info_text = info_font.render(f"Z  X C", 20, DARK_BLUE)
        screen.blit(
            info_text,
            (BORDER_SIZE + 5, HEIGHT - BORDER_SIZE - GRID_SIZE + GRID_SIZE // 4 + 112),
        )
        if fpwon:
            v_text = v_font.render("Player 1 WON!", 36, RED)
            screen.blit(
                v_text,
                (
                    WIDTH // 2 - v_text.get_width() // 2,
                    HEIGHT // 2 - v_text.get_height(),
                ),
            )
        if spwon:
            v_text = v_font.render(f"{player2_text} WON!", 36, RED)
            screen.blit(
                v_text,
                (
                    WIDTH // 2 - v_text.get_width() // 2,
                    HEIGHT // 2 - v_text.get_height(),
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
        # if 1 player mode, AI move
        if not first_player and versus_ai and not fpwon and not spwon:
            best_move = calculate_best_move(
                ball_position,
                directions,
                used_paths,
                BORDER_SIZE,
                GRID_WIDTH,
                GRID_HEIGHT,
                GRID_SIZE,
                directions2,
            )
            # move ball across the best move path
            if not first_player:
                ball_position = cpu_move(best_move)
                if win_condition(ball_position) == "first":
                    fpwon = True
                elif win_condition(ball_position) == "second":
                    spwon = True
                first_player = True

    pygame.quit()


global restarting_loop
restarting_loop = True

while restarting_loop:
    game_body()

sys.exit()
