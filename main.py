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
current_piece_position_x = COLUMNS//2
current_piece_position_y = 0

fall_timer = 0
fall_delay = 500        # Piece fall down once every 500ms
move_timer = 0
move_delay = 150         # Slide every 150ms
move_direction = 0
while running:
    dt = clock.tick(60)     #limit to 60fps
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            key_hold_timer = 0
            # Movement
            if event.key == pygame.K_a and current_piece_position_x>0:
                current_piece_position_x -= 1
                move_direction = -1
                move_timer = 0
            if event.key == pygame.K_d and current_piece_position_x<(COLUMNS-len(current_piece[0])):
                current_piece_position_x += 1
                move_direction = 1
                move_timer = 0
        if event.type == pygame.KEYUP:
            move_direction = 0
    #Update
    # Handle Fall
    fall_timer += dt
    if fall_timer > fall_delay:
        current_piece_position_y += 1
        fall_timer = 0
    key_pressed = pygame.key.get_pressed()
    # Handle sliding
    if move_direction != 0:
        move_timer += dt
        if move_timer>move_delay:
            current_piece_position_x += move_direction
            move_timer = 0

    #Draw
    screen.fill((0,0,0))
    for r in range(len(current_piece)):
        for c in range(len(current_piece[r])):
            if(current_piece[r][c] == 1):
                x = (current_piece_position_x + c) * CELL
                y = (current_piece_position_y + r) * CELL
                rect = pygame.Rect(x,y, CELL, CELL)
                pygame.draw.rect(screen, current_piece_color, rect)
    # Update display
    pygame.display.flip()
pygame.quit()