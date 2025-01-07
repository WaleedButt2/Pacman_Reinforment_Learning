import pygame
WIDTH, HEIGHT = 400,400  # Window size
TILE_SIZE = 10  # Size of each tile
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE
FPS = 20
SCREEN_WIDTH = 800  # Or any desired width
SCREEN_HEIGHT = 600  # Or any desired height
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

num_enemies=5

DIRECTIONS = {
    pygame.K_w: (-1, 0),  # Up
    pygame.K_s: (1, 0),   # Down
    pygame.K_a: (0, -1),  # Left
    pygame.K_d: (0, 1)    # Right
}