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

    return maze

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


def draw_maze(maze, player_pos, enemies):
    """Draw the maze, player, food, and enemies."""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(BLACK)
    for row in range(ROWS):
        for col in range(COLS):
            if maze[row][col] == 1:  # Wall
                pygame.draw.rect(screen, BLUE, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif maze[row][col] == 2:  # Food
                pygame.draw.circle(screen, YELLOW, (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 4)
    # Draw player
    pygame.draw.rect(screen, GREEN, (player_pos[1] * TILE_SIZE, player_pos[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy["pos"][1] * TILE_SIZE, enemy["pos"][0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))


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
    return random.choice(far_targets) if far_targets else start  # Return a random far target or stay in place


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
    """Move all enemies toward far-away targets using BFS."""
    for enemy in enemies:
        # If the enemy has no target or reached its target, assign a new far target
        if enemy["target"] is None or enemy["pos"] == enemy["target"]:
            enemy["target"] = find_far_target(maze, enemy["pos"])

        # Find the path to the target using BFS
        path = bfs_pathfinding(maze, enemy["pos"], enemy["target"])
        if path:  # If there's a valid path, move to the next step on the path
            enemy["pos"] = path[0]

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