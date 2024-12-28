def is_valid_move(grid, x, y):
    """
    Check if the move is within the grid boundaries.
    """
    return 0 <= x < len(grid) and 0 <= y < len(grid[0])


def get_possible_moves():
    """
    Returns the possible relative moves on the grid: sides, top-bottom, and diagonal.
    """
    return [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),  # Up, Down, Left, Right
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),  # Diagonals
    ]


def find_maximum_path(grid, x, y, current_path, all_paths, visited):
    """
    Recursive function to find the maximum possible path starting from (x, y).
    """
    if not is_valid_move(grid, x, y) or (x, y) in visited:
        return

    visited.add((x, y))
    current_path.append((x, y))

    # Continue until no more moves are possible
    if grid[x][y] == "bouncy()":
        for dx, dy in get_possible_moves():
            nx, ny = x + dx, y + dy
            find_maximum_path(grid, nx, ny, current_path, all_paths, visited)

    # Save the maximum path and backtrack
    all_paths.append(current_path[:])
    current_path.pop()
    visited.remove((x, y))


def get_maximum_paths_from_start(grid, start_x, start_y):
    """
    Generate all maximum paths starting from a specific cell (start_x, start_y).
    """
    all_paths = []
    visited = set()
    find_maximum_path(grid, start_x, start_y, [], all_paths, visited)

    # Remove duplicate paths
    unique_paths = []
    seen = set()
    for path in all_paths:
        path_tuple = tuple(path)
        if path_tuple not in seen:
            seen.add(path_tuple)
            unique_paths.append(path)

    return unique_paths


# Example usage
grid = [
    ["bouncy()", "empty", "bouncy()"],
    ["empty", "bouncy()", "empty"],
    ["bouncy()", "empty", "bouncy()"],
]

start_x, start_y = 0, 0  # Specify the starting point
paths = get_maximum_paths_from_start(grid, start_x, start_y)
for path in paths:
    print(path)
