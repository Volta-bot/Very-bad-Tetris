import pygame
import random
pygame.init()
## Constants     A grid in tetris is 10x20, each cell is a quare with each side = 30 pixels.
ROWS = 20
COLUMNS = 10
HEIGHT = 600 
WIDTH  = 300
CELL = 30
## Initialize board and bricks
BOARD = [[0 for i in range(COLUMNS)] for i in range(ROWS)]      #10x20 grid, initial value = 0
PIECES = [
    [[1,1,1,1]],        # I - 1
    [[1,1],[1,1]],      # O - 2
    [[1,1,1],[0,1,0]],  # T - 3
    [[0,1,1],[1,1,0]],  # S - 4
    [[1,1,0],[0,1,1]],  # Z - 5
    [[1,1,1],[1,0,0]],  # L - 6
    [[1,1,1],[0,0,1]]   # J - 7
]
PIECE_COLORS = [
    (247, 249, 249),    # I
    (243, 225, 9),      # O 
    (160, 0, 241),      # T
    (2, 241, 1),        # S
    (240, 0, 2),        # Z
    (239, 130, 1),      # L
    (1, 0, 242)         # J
]
## Initialize Pygame
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
running = True
# Initialize current piece before game starts
current_piece_index = random.randint(0,6)
current_piece_color = PIECE_COLORS[current_piece_index]
current_piece = PIECES[current_piece_index]
current_piece_position_x = COLUMNS/2
current_piece_position_y = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0,0,0))
    #
    for r in range(len(current_piece)):
        for c in range(len(current_piece[r])):
            if(current_piece[r][c] == 1):
                x = (current_piece_position_x + c) * CELL
                y = (current_piece_position_y + r) * CELL
                rect = pygame.Rect(x,y, CELL, CELL)
                pygame.draw.rect(screen, current_piece_color, rect)
    # Update display
    pygame.display.flip()
    clock.tick(60)      #limit to 60fps
pygame.quit()