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
    BORDER = 150
    G_SIZE = 55

    g_wid = 2 * x * G_SIZE
    g_hei = 2 * y * G_SIZE
    WIDTH, HEIGHT = g_wid + 2 * BORDER, g_hei + 2 * BORDER
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

    ball_pos = [x * G_SIZE + BORDER, y * G_SIZE + BORDER]
    used_paths = []
    used_paths_player1 = []  # to color only
    used_paths_player2 = []
    invisible_paths = []  # eraser (visual only)

    player_font = pygame.font.SysFont("Georgia", 36)
    v_font = pygame.font.SysFont("Cambria", 72)
    info_font = pygame.font.SysFont("Ariel", 20)

    img = pygame.image.load("ball.png")
    img = pygame.transform.scale(img, (G_SIZE * 0.5, G_SIZE * 0.5))
    first_player = True  # Turn
    fpwon = False
    spwon = False

    # Player 1
    directions = {
        "q": (-G_SIZE, -G_SIZE),
        "w": (0, -G_SIZE),
        "e": (G_SIZE, -G_SIZE),
        "a": (-G_SIZE, 0),
        "d": (G_SIZE, 0),
        "z": (-G_SIZE, G_SIZE),
        "x": (0, G_SIZE),
        "c": (G_SIZE, G_SIZE),
    }
    # Player 2
    directions2 = {
        "i": (-G_SIZE, -G_SIZE),
        "o": (0, -G_SIZE),
        "p": (G_SIZE, -G_SIZE),
        "k": (-G_SIZE, 0),
        ";": (G_SIZE, 0),
        ",": (-G_SIZE, G_SIZE),
        ".": (0, G_SIZE),
        "/": (G_SIZE, G_SIZE),
    }

    def win_condition(position):
        if position[1] == BORDER and (
            position[0] == int(g_wid / 2) + BORDER
            or position[0] == int(g_wid / 2) + BORDER - G_SIZE
            or position[0] == int(g_wid / 2) + BORDER + G_SIZE
        ):
            return "first"
        elif position[1] == BORDER + g_hei and (
            position[0] == int(g_wid / 2) + BORDER
            or position[0] == int(g_wid / 2) + BORDER - G_SIZE
            or position[0] == int(g_wid / 2) + BORDER + G_SIZE
        ):
            return "second"
        else:
            return "in progress"

    def cant_move(new_temp_pos):
        if (
            BORDER <= new_temp_pos[0] <= g_wid + BORDER
            and BORDER <= new_temp_pos[1] <= g_hei + BORDER
            and (ball_pos, new_temp_pos) not in used_paths
            and (new_temp_pos, ball_pos) not in used_paths
        ):
            return False
        return True

    def blocked():  # not for AI
        directions_available = 8
        new_pos = [ball_pos[0] - G_SIZE, ball_pos[1] - G_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_pos[0], ball_pos[1] - G_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_pos[0] + G_SIZE, ball_pos[1] - G_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_pos[0] - G_SIZE, ball_pos[1]]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_pos[0] + G_SIZE, ball_pos[1]]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_pos[0] - G_SIZE, ball_pos[1] + G_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_pos[0], ball_pos[1] + G_SIZE]
        if cant_move(new_pos):
            directions_available = directions_available - 1
        new_pos = [ball_pos[0] + G_SIZE, ball_pos[1] + G_SIZE]
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
    for i in range(G_SIZE, g_hei - G_SIZE, G_SIZE):
        spos = [BORDER, i + BORDER]
        endpos = [BORDER, i + BORDER + G_SIZE]
        pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
        used_paths.append((spos, endpos))

        spos = [g_wid + BORDER, i + BORDER]
        endpos = [g_wid + BORDER, i + BORDER + G_SIZE]
        pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
        used_paths.append((spos, endpos))

    # Draw middle line
    for i in range(BORDER, g_wid + BORDER, G_SIZE):
        spos = [i, BORDER + (g_hei) / 2]
        endpos = [i + G_SIZE, BORDER + g_hei / 2]
        pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
        used_paths.append((spos, endpos))

    for i in range(BORDER, BORDER + int(g_wid / 2) - G_SIZE, G_SIZE):
        spos = [i, BORDER + G_SIZE]
        endpos = [i + G_SIZE, BORDER + G_SIZE]
        endpos2 = [i + G_SIZE, BORDER]
        endpos3 = [i, BORDER]
        startpos2 = [i + G_SIZE, BORDER + G_SIZE]
        pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
        used_paths.append((spos, endpos))
        used_paths.append((spos, endpos2))
        used_paths.append((spos, endpos3))
        used_paths.append((startpos2, endpos3))
        invisible_paths.append((spos, endpos2))
        invisible_paths.append((spos, endpos3))
        invisible_paths.append((startpos2, endpos3))

    for i in range(
        int(g_wid / 2) + G_SIZE + BORDER,
        g_wid + BORDER,
        G_SIZE,
    ):
        spos = [i, BORDER + G_SIZE]
        endpos = [i + G_SIZE, BORDER + G_SIZE]
        endpos2 = [i + G_SIZE, BORDER]
        startpos2 = [i + G_SIZE, BORDER + G_SIZE]
        endpos3 = [i, BORDER]
        pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
        used_paths.append((spos, endpos))
        used_paths.append((spos, endpos2))
        used_paths.append((startpos2, endpos2))
        used_paths.append((startpos2, endpos3))
        invisible_paths.append((spos, endpos2))
        invisible_paths.append((startpos2, endpos2))
        invisible_paths.append((startpos2, endpos3))

    for i in range(BORDER, int(g_wid / 2) + BORDER - G_SIZE, G_SIZE):
        spos = [i, g_hei + BORDER - G_SIZE]
        endpos = [i + G_SIZE, g_hei + BORDER - G_SIZE]
        endpos2 = [i + G_SIZE, g_hei + BORDER]
        endpos3 = [i, g_hei + BORDER]
        startpos2 = [i + G_SIZE, g_hei + BORDER - G_SIZE]
        pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
        used_paths.append((spos, endpos))
        used_paths.append((spos, endpos2))
        used_paths.append((spos, endpos3))
        used_paths.append((startpos2, endpos3))
        invisible_paths.append((spos, endpos2))
        invisible_paths.append((spos, endpos3))
        invisible_paths.append((startpos2, endpos3))

    for i in range(
        int(g_wid / 2) + G_SIZE + BORDER,
        g_wid + BORDER,
        G_SIZE,
    ):
        spos = [i, g_hei + BORDER - G_SIZE]
        endpos = [i + G_SIZE, g_hei + BORDER - G_SIZE]
        endpos2 = [i + G_SIZE, g_hei + BORDER]
        startpos2 = [i + G_SIZE, g_hei + BORDER - G_SIZE]
        endpos3 = [i, g_hei + BORDER]
        pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
        used_paths.append((spos, endpos))
        used_paths.append((spos, endpos2))
        used_paths.append((startpos2, endpos2))
        used_paths.append((startpos2, endpos3))
        invisible_paths.append((spos, endpos2))
        invisible_paths.append((startpos2, endpos2))
        invisible_paths.append((startpos2, endpos3))

    # top goal
    spos = [int(g_wid / 2) + G_SIZE + BORDER, BORDER]
    endpos = [int(g_wid / 2) + G_SIZE + BORDER, BORDER + G_SIZE]
    pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
    used_paths.append((spos, endpos))
    spos = [int(g_wid / 2) - G_SIZE + BORDER, BORDER]
    endpos = [int(g_wid / 2) - G_SIZE + BORDER, BORDER + G_SIZE]
    pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
    used_paths.append((spos, endpos))
    # bottom goal
    spos = [int(g_wid / 2) + G_SIZE + BORDER, g_hei + BORDER - G_SIZE]
    endpos = [int(g_wid / 2) + G_SIZE + BORDER, g_hei + BORDER]
    pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
    used_paths.append((spos, endpos))
    spos = [int(g_wid / 2) - G_SIZE + BORDER, g_hei + BORDER - G_SIZE]
    endpos = [int(g_wid / 2) - G_SIZE + BORDER, g_hei + BORDER]
    pygame.draw.line(screen, DARK_BLUE, spos, endpos, 3)
    used_paths.append((spos, endpos))

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
                if (key in directions and first_player and not spwon) or (
                    key in directions2 and not first_player and not fpwon
                ):
                    if first_player:
                        new_pos = [
                            ball_pos[0] + directions[key][0],
                            ball_pos[1] + directions[key][1],
                        ]
                    else:
                        new_pos = [
                            ball_pos[0] + directions2[key][0],
                            ball_pos[1] + directions2[key][1],
                        ]

                    # Check if the new position is within bounds and not already used
                    if (
                        BORDER <= new_pos[0] <= g_wid + BORDER
                        and BORDER <= new_pos[1] <= g_hei + BORDER
                        and (ball_pos, new_pos) not in used_paths
                        and (new_pos, ball_pos) not in used_paths
                    ):
                        #   check if move ended on free spot, if so, switch player
                        change = False
                        if not any(new_pos in path for path in used_paths):
                            change = True
                        # separate paths for playes 1/2 for recoloring only
                        if first_player:
                            used_paths_player1.append((ball_pos, new_pos))
                        elif not first_player:
                            used_paths_player2.append((ball_pos, new_pos))

                        used_paths.append((ball_pos, new_pos))
                        play_sound("kick")
                        if win_condition(new_pos) == "first":
                            fpwon = True
                        elif win_condition(new_pos) == "second":
                            spwon = True

                        if change:
                            first_player = not first_player

                        ball_pos = new_pos
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
        for x in range(BORDER - 5 * G_SIZE, WIDTH, G_SIZE):
            pygame.draw.line(screen, PALE_BLUE, (x, 0), (x, HEIGHT))
        for y in range(BORDER - 5 * G_SIZE, HEIGHT, G_SIZE):
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
        rect.center = ball_pos
        screen.blit(img, rect)

        player_font.bold = True
        player_font.italic = True
        v_font.bold = True
        p1_text = player_font.render("Player 1", 36, GREEN)
        p2_text = player_font.render(player2_text, 36, BLUE)

        if player2_text == "Player 2":
            info_text = info_font.render("I  O  P", 20, DARK_BLUE)
            screen.blit(
                info_text, (WIDTH - 2 * BORDER + 5, BORDER - 1.75 * G_SIZE + 95)
            )
            info_text = info_font.render("K      ;  -  to move", 20, DARK_BLUE)
            screen.blit(
                info_text, (WIDTH - 2 * BORDER + 5, BORDER - 1.75 * G_SIZE + 113)
            )
            info_text = info_font.render(",   .   /", 20, DARK_BLUE)
            screen.blit(
                info_text, (WIDTH - 2 * BORDER + 5, BORDER - 1.75 * G_SIZE + 131)
            )

        info_text = info_font.render("ESC to quit", 20, DARK_BLUE)
        screen.blit(info_text, (BORDER + 5, HEIGHT - BORDER - 0.75 * G_SIZE))
        info_text = info_font.render("F5 to restart", 20, DARK_BLUE)
        screen.blit(info_text, (BORDER + 5, HEIGHT - BORDER - 0.75 * G_SIZE + 24))
        info_text = info_font.render("F3 to switch to versus CPU", 20, DARK_BLUE)
        screen.blit(info_text, (BORDER + 5, HEIGHT - BORDER - 0.75 * G_SIZE + 48))
        info_text = info_font.render("Q W E", 20, DARK_BLUE)
        screen.blit(info_text, (BORDER + 5, HEIGHT - BORDER - 0.75 * G_SIZE + 72))
        info_text = info_font.render("A     D  -  to move", 20, DARK_BLUE)
        screen.blit(info_text, (BORDER + 5, HEIGHT - BORDER - 0.75 * G_SIZE + 92))
        info_text = info_font.render("Z  X C", 20, DARK_BLUE)
        screen.blit(info_text, (BORDER + 5, HEIGHT - BORDER - 0.75 * G_SIZE + 112))

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
            (half_w + G_SIZE * 1.5, HEIGHT - BORDER - G_SIZE * 0.8),
        )
        screen.blit(
            p2_text,
            (
                half_w - G_SIZE * 1.5 - p2_text.get_width(),
                BORDER + G_SIZE - G_SIZE * 0.8,
            ),
        )

        pygame.display.flip()
        clock.tick(FPS)
        # if 1 player mode, AI move
        if not first_player and versus_ai and not fpwon and not spwon:
            best_move = calculate_best_move(
                ball_pos, directions, used_paths, BORDER, g_wid, g_hei, G_SIZE
            )
            # move ball across the best move path
            if not first_player:
                ball_pos = cpu_move(best_move)
                if win_condition(ball_pos) == "first":
                    fpwon = True
                elif win_condition(ball_pos) == "second":
                    spwon = True
                first_player = True

    pygame.quit()


global restarting_loop
restarting_loop = True

while restarting_loop:
    game_body()

sys.exit()
