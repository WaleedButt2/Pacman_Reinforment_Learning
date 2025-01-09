from constants import *
import pygame
import random
from collections import deque
import numpy as np
def create_maze(rows, cols):
    """Create a Pac-Man-like maze with guaranteed movement freedom and open edges."""
    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    # Create paths and loops
    for row in range(1, rows - 1):
        for col in range(1, cols - 1):
            maze[row][col] = 0

    # Add walls to create loops and sections
    for i in range(2, rows - 2, 4):  # Horizontal walls
        for j in range(1, cols - 1):
            if random.random() < 0.7:
                maze[i][j] = 1

    for i in range(2, cols - 2, 4):  # Vertical walls
        for j in range(1, rows - 1):
            if random.random() < 0.7:
                maze[j][i] = 1

    # Remove chunks of walls
    remove_wall_chunks(maze, chunk_size=5, remove_fraction=0.6)

    # Ensure all edges are open
    for col in range(cols):
        maze[0][col] = 0  # Top edge
        maze[rows - 1][col] = 0  # Bottom edge
    for row in range(rows):
        maze[row][0] = 0  # Left edge
        maze[row][cols - 1] = 0  # Right edge

    # Ensure food is accessible
    ensure_accessible(maze)

    # Place food everywhere except walls
    for row in range(rows):
        for col in range(cols):
            if maze[row][col] == 0:
                maze[row][col] = 2  # Food

    return np.array(maze)

def partition_maze_optimized(maze, s):
    x, y = s
    rows, cols = len(maze), len(maze[0])
    half_grid = 5 // 2

    partition = [
        [
            maze[(x + dx) % rows][(y + dy) % cols]
            for dy in range(-half_grid, half_grid + 1)
        ]
        for dx in range(-half_grid, half_grid + 1)
    ]
    return np.array(partition)

def remove_wall_chunks(maze, chunk_size, remove_fraction):
    """
    Randomly remove chunks of walls.
    :param maze: The maze grid.
    :param chunk_size: Size of each chunk (e.g., 5x5).
    :param remove_fraction: Fraction of chunks to remove (0 to 1).
    """
    rows, cols = len(maze), len(maze[0])
    chunk_rows, chunk_cols = rows // chunk_size, cols // chunk_size

    # Create a list of all chunks
    chunks = [
        (r * chunk_size, c * chunk_size)
        for r in range(chunk_rows)
        for c in range(chunk_cols)
    ]

    # Randomly select chunks to remove
    num_chunks_to_remove = int(len(chunks) * remove_fraction)
    chunks_to_remove = random.sample(chunks, num_chunks_to_remove)

    for start_row, start_col in chunks_to_remove:
        for row in range(start_row, min(start_row + chunk_size, rows)):
            for col in range(start_col, min(start_col + chunk_size, cols)):
                maze[row][col] = 0  # Remove wall in this chunk



def ensure_accessible(maze):
    """Ensure all open spaces in the maze are connected."""
    visited = set()
    queue = deque([(1, 1)])  # Start from the top-left corner
    visited.add((1, 1))

    while queue:
        current = queue.popleft()
        for direction in DIRECTIONS.values():
            neighbor = move_entity(current, direction)
            if (
                0 <= neighbor[0] < ROWS
                and 0 <= neighbor[1] < COLS
                and neighbor not in visited
                and maze[neighbor[0]][neighbor[1]] == 0
            ):
                visited.add(neighbor)
                queue.append(neighbor)

    # Remove isolated walls (any 0 not visited is inaccessible)
    for row in range(ROWS):
        for col in range(COLS):
            if maze[row][col] == 0 and (row, col) not in visited:
                maze[row][col] = 1  # Turn inaccessible space into a wall

def draw_all_games(games):
    """Draw all game instances on the screen arranged in a grid."""
    screen = pygame.display.get_surface()
    screen.fill(BLACK)  # Clear the screen before drawing

    # Arrange games in a grid
    grid_rows = 1
    grid_cols = 1
    game_width = SCREEN_WIDTH / grid_cols
    game_height = SCREEN_HEIGHT / grid_rows
    for index, game in enumerate(games):
        row = index // grid_cols
        col = index % grid_cols
        x_offset = col * game_width
        y_offset = row * game_height
        draw_maze(game.maze, game.player_pos, game.enemies, x_offset, y_offset, game_width, game_height)


def draw_maze(maze, player_pos, enemies, x_offset=0, y_offset=0, game_width=SCREEN_WIDTH, game_height=SCREEN_HEIGHT):
    """Draw the maze, player, food, and enemies in a specified area."""
    screen = pygame.display.get_surface()  # Get the main display surface

    # Calculate cell sizes based on the game area dimensions
    cell_width = game_width / COLS
    cell_height = game_height / ROWS

    # Draw the maze grid
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(
                x_offset + col * cell_width,
                y_offset + row * cell_height,
                cell_width,
                cell_height
            )
            if maze[row][col] == 1:  # Wall
                pygame.draw.rect(screen, BLUE, rect)
            elif maze[row][col] == 2:  # Food
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (int(rect.centerx), int(rect.centery)),
                    min(cell_width, cell_height) // 4
                )
            else:
                # Optional: Draw floor or empty space
                pygame.draw.rect(screen, BLACK, rect)

    # Draw player as a circle
    player_center = (
        int(x_offset + player_pos[1] * cell_width + cell_width / 2),
        int(y_offset + player_pos[0] * cell_height + cell_height / 2),
    )
    pygame.draw.circle(screen, GREEN, player_center, min(cell_width, cell_height) // 1.5)

    # Draw enemies as triangles
    for enemy in enemies:
        enemy_center_x = x_offset + enemy["pos"][1] * cell_width + cell_width / 2
        enemy_center_y = y_offset + enemy["pos"][0] * cell_height + cell_height / 2
        enemy_radius = min(cell_width, cell_height) // 1.5

        # Define the triangle points
        triangle_points = [
            (enemy_center_x, enemy_center_y - enemy_radius),  # Top
            (enemy_center_x - enemy_radius, enemy_center_y + enemy_radius),  # Bottom-left
            (enemy_center_x + enemy_radius, enemy_center_y + enemy_radius),  # Bottom-right
        ]
        pygame.draw.polygon(screen, RED, triangle_points)


def move_entity(pos, direction):
    """Move an entity (player or enemy) with wrap-around logic."""
    new_row = (pos[0] + direction[0]) % ROWS  # Wrap around vertically
    new_col = (pos[1] + direction[1]) % COLS  # Wrap around horizontally
    return (new_row, new_col)


def is_valid_move(pos, maze):
    """Check if a move is valid."""
    return maze[pos[0]][pos[1]] != 1



def find_far_target(maze, start, distance_threshold=15):
    """Find a random valid target far away from the start position."""
    far_targets = []
    for row in range(ROWS):
        for col in range(COLS):
            if maze[row][col] == 0:  # Valid open space
                distance = abs(start[0] - row) + abs(start[1] - col)  # Manhattan distance
                if distance >= distance_threshold:
                    far_targets.append((row, col))
    if far_targets:
        return random.choice(far_targets)
    else:
        # If no far targets found, reduce the threshold
        #print("No far targets found. Reducing distance threshold.")
        return find_near_target(maze, start, distance_threshold)

def find_near_target(maze, start, distance_threshold):
    """Find a valid target closer to the start position."""
    for threshold in range(distance_threshold - 1, 0, -1):
        near_targets = []
        for row in range(ROWS):
            for col in range(COLS):
                if maze[row][col] == 0:
                    distance = abs(start[0] - row) + abs(start[1] - col)
                    if distance == threshold:
                        near_targets.append((row, col))
        if near_targets:
            return random.choice(near_targets)
    # If no targets found, return the starting position
    return start



def bfs_pathfinding(maze, start, target):
    """Find the shortest path from start to target using BFS."""
    queue = deque([(start, [])])  # Queue holds tuples of (current_position, path_to_position)
    visited = set()  # Keep track of visited positions
    visited.add(start)

    while queue:
        current, path = queue.popleft()
        if current == target:
            return path  # Return the path to the target

        for direction in DIRECTIONS.values():
            neighbor = move_entity(current, direction)
            if neighbor not in visited and is_valid_move(neighbor, maze):
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return []  # Return empty path if no valid path found

def move_enemies(enemies, maze):
    for enemy in enemies:
        # If the enemy has no target or reached its target, assign a new far target
        if enemy["target"] is None or enemy["pos"] == enemy["target"]:
            enemy["target"] = find_far_target(maze, enemy["pos"])
            #print(f"Enemy at {enemy['pos']} assigned new target {enemy['target']}")

        # Find the path to the target using BFS
        path = bfs_pathfinding(maze, enemy["pos"], enemy["target"])
        if path:
            enemy["pos"] = path[0]
            #print(f"Enemy moved to {enemy['pos']}")
        else:
            #print(f"Enemy at {enemy['pos']} could not find a path to {enemy['target']}, moving randomly.")
            # Move randomly
            valid_moves = [direction for direction in DIRECTIONS.values()
                           if is_valid_move(move_entity(enemy["pos"], direction), maze)]
            if valid_moves:
                enemy["pos"] = move_entity(enemy["pos"], random.choice(valid_moves))
                #print(f"Enemy moved randomly to {enemy['pos']}")
            else:
                pass
                #print(f"Enemy at {enemy['pos']} is stuck.")
            # Assign a new target
            enemy["target"] = None



def get_reward(state, maze):
    row, col = state
    if maze[row][col] == 2:  # Food
        return 10
    elif maze[row][col] == 1:  # Wall
        return -1
    elif maze[row][col] == 'E':
        return -100
    else:
        return -0.1
def print_maze_with_entities(maze, player_pos, enemies):
    """
    Print the maze to the console with player and enemies represented.
    Player: 'P'
    Enemies: 'E'
    Walls: '#'
    Food: 'o'
    Empty space: '.'
    """
    # Create a copy of the maze to overlay entities
    maze_copy = [[cell for cell in row] for row in maze]


    # Place the player
    maze_copy[player_pos[0]][player_pos[1]] = 'P'
    
    # Place the enemies
    for enemy in enemies:
        row, col = enemy["pos"]
        maze_copy[row][col] = 'E'
    
    # Print the maze
    for row in maze_copy:
        print("".join(
            "#" if cell == 1 else 
            "o" if cell == 2 else 
            "P" if cell == 'P' else 
            "E" if cell == 'E' else 
            "." for cell in row
        ))
    print("\n" + "=" * 50 + "\n")  # Separator for frames

def extract_view(maze, player_pos, size=4):
    view_range = size // 2  # Half the size for the square area
    player_row, player_col = player_pos

    maze_height = len(maze)
    maze_width = len(maze[0])

    # Determine the slicing boundaries
    start_row = max(player_row - view_range, 0)
    end_row = min(player_row + view_range, maze_height - 1) + 1
    start_col = max(player_col - view_range, 0)
    end_col = min(player_col + view_range, maze_width - 1) + 1

    # Extract the sliced grid
    sliced_view = [row[start_col:end_col] for row in maze[start_row:end_row]]

    # Add padding if necessary to ensure 4x4 size
    while len(sliced_view) < size:  # Pad rows to make it 4x4
        if start_row == 0:  # Add empty rows at the bottom if near the top edge
            sliced_view.append(['#'] * len(sliced_view[0]))
        else:  # Add empty rows at the top if near the bottom edge
            sliced_view.insert(0, ['#'] * len(sliced_view[0]))

    for row in sliced_view:  # Pad columns in each row
        while len(row) < size:
            if start_col == 0:  # Add walls to the right if near the left edge
                row.append('#')
            else:  # Add walls to the left if near the right edge
                row.insert(0, '#')

    return sliced_view