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
    [[]],
    [[1,1,1,1]],        # I - 1
    [[1,1],[1,1]],      # O - 2
    [[1,1,1],[0,1,0]],  # T - 3
    [[0,1,1],[1,1,0]],  # S - 4
    [[1,1,0],[0,1,1]],  # Z - 5
    [[1,1,1],[1,0,0]],  # L - 6
    [[1,1,1],[0,0,1]]   # J - 7
]
PIECE_COLORS = [
    (),
    (33, 205, 255),     # I
    (253, 218, 29),     # O 
    (178, 49, 240),     # T
    (235, 0, 69),       # S
    (61, 202, 49),      # Z
    (255, 131, 0),      # L
    (15, 108, 242)      # J
]
GHOST_COLOR = (153, 153, 153)
## Functions
def check_collision(piece, pos_x, pos_y):
    global BOARD
    for r in range(len(piece)):
        for c in range(len(piece[r])):
            if piece[r][c] != 0:
                board_x = pos_x + c
                board_y = pos_y + r
                if board_x < 0 or board_x >= COLUMNS: 
                    return True
                if board_y >= ROWS:
                    return True
                if BOARD[board_y][board_x] != 0:    # A piece is already under
                    return True
    return False            
def rotate(piece):
    return [list(row)[::-1] for row in zip(*piece)]
def lock_into_board():
    global current_piece, current_piece_position_x, current_piece_position_y, BOARD
    for r in range(len(current_piece)):
        for c in range(len(current_piece[r])):
            if current_piece[r][c] != 0:
                board_x = current_piece_position_x + c
                board_y = current_piece_position_y + r
                BOARD[board_y][board_x] = current_piece_index
def spawn_new_piece():
    global current_piece_index, current_piece_color, current_piece, current_piece_position_x, current_piece_position_y, running
    global piece_bag
    if not piece_bag:   # piece bag is empty -> shuffle a new bag
        piece_bag = list(range(1,8))
        random.shuffle(piece_bag)
    current_piece_index = piece_bag.pop()
    current_piece_color = PIECE_COLORS[current_piece_index]
    current_piece = PIECES[current_piece_index]
    current_piece_position_x = COLUMNS//2 - len(current_piece[0])//2
    current_piece_position_y = 0
    if(check_collision(current_piece,current_piece_position_x,current_piece_position_y)):   # Game over
        running = False
def clear_line():
    global BOARD
    new_board = []
    cleared_rows = 0
    for row in BOARD:
        if 0 in row:
            new_board.append(row)
        else:
            cleared_rows += 1
    for i in range(cleared_rows):
        new_board.insert(0, [0]*COLUMNS)
    BOARD = new_board 
    return cleared_rows
def calculate_points(cleared_lines):
    global current_score
    multiplier = 0
    match cleared_lines:
        case 1:
            multiplier = 1
        case 2:
            multiplier = 1.2
        case 3:
            multiplier = 1.4
        case 4:
            multiplier = 1.6
    current_score += cleared_lines * 100 * multiplier
## Initialize Pygame
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()
running = True
# Initialize current piece before game starts
current_piece_index = random.randint(1,7)
current_piece_color = PIECE_COLORS[current_piece_index]
current_piece = PIECES[current_piece_index]
current_piece_position_x = COLUMNS//2 - len(current_piece[0])//2
current_piece_position_y = 0

fall_timer = 0
fall_delay = 500        # Piece fall down once every 500ms
move_timer = 0

time_hold = 0
slide_delay = 300       # Starts sliding after holding for 300ms

move_timer = 0
move_delay = 150        # Slide every 150ms
move_direction = 0

current_score = 0
piece_bag =[]
while running:
    dt = clock.tick(60)     #limit to 60fps
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Movement
            if event.key == pygame.K_a and not check_collision(current_piece,current_piece_position_x-1,current_piece_position_y):
                current_piece_position_x -= 1
                move_direction = -1
                move_timer = 0
            elif event.key == pygame.K_d and not check_collision(current_piece,current_piece_position_x+1, current_piece_position_y):
                current_piece_position_x += 1
                move_direction = 1
                move_timer = 0
            elif event.key ==  pygame.K_s:
                fall_delay = 150
            elif event.key == pygame.K_w:
                while not check_collision(current_piece, current_piece_position_x, current_piece_position_y+1):
                    current_piece_position_y += 1
                fall_timer = 0
                lock_into_board()
                cleared_lines = clear_line()
                spawn_new_piece()
                calculate_points(cleared_lines)
            elif event.key == pygame.K_r:
                rotated_piece = rotate(current_piece)
                if not check_collision(rotated_piece,current_piece_position_x,current_piece_position_y):
                    current_piece = rotated_piece
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_d:
                time_hold = 0
                move_direction = 0
            if event.key == pygame.K_s:
                fall_delay = 500
# Game logic
    # Handle sliding
    if move_direction != 0: 
        time_hold += dt
        if(time_hold > slide_delay):
            move_timer += dt
            if(move_timer>move_delay and not check_collision(current_piece, current_piece_position_x + move_direction,current_piece_position_y)):
                current_piece_position_x += move_direction
                move_timer = 0    
    # Handle fall and check collision
    fall_timer += dt
    cleared_lines = 0
    if fall_timer > fall_delay:
        fall_timer = 0
        if check_collision(current_piece, current_piece_position_x, current_piece_position_y+1):
            lock_into_board()
            cleared_lines = clear_line()
            spawn_new_piece()
            calculate_points(cleared_lines)
        else:
            current_piece_position_y += 1    
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
    # Draw ghost block (prediction)
    ghost_position_y = current_piece_position_y
    while not check_collision(current_piece, current_piece_position_x, ghost_position_y+1):
        ghost_position_y += 1
    for r in range(len(current_piece)):
        for c in range(len(current_piece[r])):
            if current_piece[r][c] != 0:
                x = (current_piece_position_x + c) * CELL
                y = (ghost_position_y + r) * CELL
                rect = pygame.Rect(x,y,CELL,CELL)
                pygame.draw.rect(screen, GHOST_COLOR, rect)
    # Draw board
    for r in range(ROWS):
        for c in range(COLUMNS):
            if BOARD[r][c] != 0:
                rect = pygame.Rect(c*CELL,r*CELL,CELL,CELL)
                pygame.draw.rect(screen, PIECE_COLORS[BOARD[r][c]], rect)
# Update display
    pygame.display.flip()
pygame.quit()
