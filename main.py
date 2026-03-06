import pygame
import random
pygame.init()
## Constants     A grid in tetris is 10x20, each cell is a quare with each side = 30 pixels.
ROWS = 20
COLUMNS = 10
HEIGHT = 600 
WIDTH  = 300
CELL = 30
## Functions
def check_collision():
    global current_piece, current_piece_position_x, current_piece_position_y
    for r in range(len(current_piece)):
        for c in range(len(current_piece[r])):
            if current_piece[r][c] != 0:
                board_x = current_piece_position_x + c
                board_y = current_piece_position_y + r + 1
                if board_y >= ROWS:
                    return True
                if BOARD[board_y][board_x] != 0:    # A piece is already under
                    return True
    return False            

def lock_into_board():
    global current_piece, current_piece_position_x, current_piece_position_y
    for r in range(len(current_piece)):
        for c in range(len(current_piece[r])):
            if current_piece[r][c] != 0:
                board_x = current_piece_position_x + c
                board_y = current_piece_position_y + r
                BOARD[board_y][board_x] = current_piece_index
def spawn_new_piece():
    global current_piece_index, current_piece_color, current_piece, current_piece_position_x, current_piece_position_y
    current_piece_index = random.randint(0,6)
    current_piece_color = PIECE_COLORS[current_piece_index]
    current_piece = PIECES[current_piece_index]
    current_piece_position_x = COLUMNS//2
    current_piece_position_y = 0
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

time_hold = 0
slide_delay = 300       # Starts sliding after holding for 300ms

move_timer = 0
move_delay = 150        # Slide every 150ms
move_direction = 0


while running:
    dt = clock.tick(60)     #limit to 60fps
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Movement
            if event.key == pygame.K_a and current_piece_position_x>0:
                current_piece_position_x -= 1
                move_direction = -1
                move_timer = 0
            elif event.key == pygame.K_d and current_piece_position_x<(COLUMNS-len(current_piece[0])):
                current_piece_position_x += 1
                move_direction = 1
                move_timer = 0
            elif event.key ==  pygame.K_s:
                fall_delay = 150
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_d:
                time_hold = 0
                move_direction = 0
            if event.key == pygame.K_s:
                fall_delay = 500
# Update
    # Handle Fall
    fall_timer += dt
    if fall_timer > fall_delay:
        fall_timer = 0
        if check_collision():
            lock_into_board()
            spawn_new_piece()
        else:
            current_piece_position_y += 1
    key_pressed = pygame.key.get_pressed()
    # Handle sliding
    if move_direction != 0: 
        time_hold += dt
        if(time_hold > slide_delay):
            move_timer += dt
            if(move_timer>move_delay and current_piece_position_x > 0 and current_piece_position_x < COLUMNS - len(current_piece[0])):
                current_piece_position_x += move_direction
                move_timer = 0
#Draw
    screen.fill((0,0,0))
    # Draw current piece
    for r in range(len(current_piece)):
        for c in range(len(current_piece[r])):
            if(current_piece[r][c] == 1):
                x = (current_piece_position_x + c) * CELL
                y = (current_piece_position_y + r) * CELL
                rect = pygame.Rect(x,y, CELL, CELL)
                pygame.draw.rect(screen, current_piece_color, rect)
    # Draw board
    for r in range(ROWS):
        for c in range(COLUMNS):
            if BOARD[r][c] != 0:
                rect = pygame.Rect(c*CELL,r*CELL,CELL,CELL)
                pygame.draw.rect(screen, PIECE_COLORS[BOARD[r][c]], rect)
# Update display
    pygame.display.flip()
pygame.quit()
