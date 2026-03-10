import pygame
import random
pygame.init()
# Constants     A grid in tetris is 10x20, each cell is a quare with each side = 30 pixels.
# BOARD
ROWS = 20
COLUMNS = 10
HEIGHT = 600 
WIDTH_BOARD  = 300
CELL = 30
SMALL_CELL = 20
# Other UI elements
WIDTH_LEFT = 150
WIDTH_RIGHT = 150
# Initialize board and bricks
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
# Functions
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
def rotate(piece,isRight):
    global lock_timer
    lock_timer = 0
    if isRight == True:
        return [list(row)[::-1] for row in zip(*piece)]
    else:
        return [list(row) for row in zip(*piece)][::-1]
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
    global current_piece_bag, next_piece_bag, canHold, fall_timer, lock_reset_counter
    canHold = True
    fall_timer = 0
    lock_reset_counter = 0
    if not current_piece_bag:   # current piece bag is empty -> shuffle a new bag
        current_piece_bag = next_piece_bag
        next_piece_bag = list(range(1,8))
        random.shuffle(next_piece_bag)
    current_piece_index = current_piece_bag.pop()
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
# Initialize Pygame
screen = pygame.display.set_mode((WIDTH_BOARD+WIDTH_LEFT+WIDTH_RIGHT,HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font("assets/font/Ithaca-LVB75.ttf",size = 32)
main_UI = pygame.image.load("assets/UI/Main_UI.png")
running = True
# Initialize current piece before game starts
current_piece_index = random.randint(1,7)
current_piece_color = PIECE_COLORS[current_piece_index]
current_piece = PIECES[current_piece_index]
current_piece_position_x = COLUMNS//2 - len(current_piece[0])//2
current_piece_position_y = 0

fall_timer = 0
fall_delay = 800            # Time between each fall
soft_drop_multiplier = 10   # Speed increase when holding softdrop button
fall_delay_temp = 0         # Used to store the current fall delay before pressing softdrop button
total_line_cleared = 0
level = 0

time_hold = 0
slide_delay = 200       # Starts sliding after holding for 300ms

move_timer = 0
move_delay = 100        # Slide every 150ms
move_direction = 0

lock_delay = 500        #lock into board after 500ms
lock_timer = 0

max_lock_reset = 15
lock_reset_counter = 0

current_score = 0
current_piece_bag =[]
next_piece_bag = list(range(1,8))
random.shuffle(next_piece_bag)

isHolding = False
hold_piece_index = 0
canHold = True
while running:
    dt = clock.tick(60)     #limit to 60fps
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Move left/right
            if event.key == pygame.K_LEFT and not check_collision(current_piece,current_piece_position_x-1,current_piece_position_y):
                if lock_reset_counter < 15 and check_collision(current_piece, current_piece_position_x,current_piece_position_y+1):
                    lock_timer = 0
                    lock_reset_counter += 1
                current_piece_position_x -= 1
                move_direction = -1
                move_timer = 0
            elif event.key == pygame.K_RIGHT and not check_collision(current_piece,current_piece_position_x+1, current_piece_position_y):
                if lock_reset_counter < 15 and check_collision(current_piece, current_piece_position_x,current_piece_position_y+1):
                    lock_timer = 0
                    lock_reset_counter += 1
                current_piece_position_x += 1
                move_direction = 1
                move_timer = 0
            # Soft drop
            elif event.key ==  pygame.K_DOWN:
                fall_delay_temp = fall_delay
                fall_delay = max(50,fall_delay/soft_drop_multiplier)
            # Hard drop
            elif event.key == pygame.K_UP:
                while not check_collision(current_piece, current_piece_position_x, current_piece_position_y+1):
                    current_piece_position_y += 1
                fall_timer = 0
                lock_into_board()
                cleared_lines = clear_line()
                total_line_cleared += cleared_lines
                level = total_line_cleared//10
                fall_delay = max(50,800 - level*60) #minimum delay is 50ms
                spawn_new_piece()
                calculate_points(cleared_lines)
            # Rotate piece (clock wise/counter clock wise)
            elif event.key == pygame.K_c:
                if lock_reset_counter < 15 and check_collision(current_piece, current_piece_position_x,current_piece_position_y+1):
                    lock_timer = 0
                    lock_reset_counter += 1
                rotated_piece = rotate(current_piece,True)
                if not check_collision(rotated_piece,current_piece_position_x,current_piece_position_y):
                    current_piece = rotated_piece
            elif event.key == pygame.K_z:
                if lock_reset_counter < 15 and check_collision(current_piece, current_piece_position_x,current_piece_position_y+1):
                    lock_timer = 0
                    lock_reset_counter += 1
                rotated_piece = rotate(current_piece,False)
                if not check_collision(rotated_piece,current_piece_position_x,current_piece_position_y):
                    current_piece = rotated_piece
            # Hold piece
            elif event.key == pygame.K_x and canHold:
                canHold = False
                if isHolding:
                    temp = current_piece_index
                    current_piece_index = hold_piece_index
                    hold_piece_index = temp

                    current_piece_color=PIECE_COLORS[current_piece_index]
                    current_piece = PIECES[current_piece_index]

                    current_piece_position_x = COLUMNS//2 - len(current_piece[0])//2
                    current_piece_position_y = 0
                else:
                    isHolding = True
                    hold_piece_index = current_piece_index
                    spawn_new_piece()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                time_hold = 0
                move_direction = 0
            if event.key == pygame.K_DOWN:
                fall_delay = fall_delay_temp        # restore the previous fall delay
# Game logic
    # Get move direction
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        move_direction = -1
    elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
        move_direction = 1
    else:
        move_direction = 0
    # Handle sliding
    if move_direction != 0: 
        time_hold += dt
        if(time_hold > slide_delay):
            move_timer += dt
            if(move_timer>move_delay and not check_collision(current_piece, current_piece_position_x + move_direction,current_piece_position_y)):
                current_piece_position_x += move_direction
                move_timer = 0    
                if lock_reset_counter < 15 and check_collision(current_piece, current_piece_position_x,current_piece_position_y+1):
                    lock_timer = 0
                    lock_reset_counter += 1                 
    # Gravity
    fall_timer += dt
    cleared_lines = 0
    if fall_timer > fall_delay and not check_collision(current_piece,current_piece_position_x,current_piece_position_y+1):
        fall_timer = 0
        current_piece_position_y += 1 
    # Lock into board
    if check_collision(current_piece,current_piece_position_x,current_piece_position_y+1):
        lock_timer += dt
        if lock_timer > lock_delay:         # lock in after 500ms delay
            lock_into_board()
            cleared_lines = clear_line()
            total_line_cleared += cleared_lines
            level = total_line_cleared//10
            fall_delay = max(50,800 - level*60) #minimum delay is 50ms
            calculate_points(cleared_lines)
            spawn_new_piece()
    else:
        lock_timer = 0   
# Draw
    screen.fill((0,0,0))    # reset the screen
    screen.blit(main_UI,(0,0))
    # Draw ghost block (prediction)
    ghost_position_y = current_piece_position_y
    while not check_collision(current_piece, current_piece_position_x, ghost_position_y+1):
        ghost_position_y += 1
    for r in range(len(current_piece)):
        for c in range(len(current_piece[r])):
            if current_piece[r][c] != 0:
                x = WIDTH_LEFT + (current_piece_position_x + c) * CELL
                y = (ghost_position_y + r) * CELL
                rect = pygame.Rect(x,y,CELL,CELL)
                pygame.draw.rect(screen, GHOST_COLOR, rect)
    # Draw current piece
    for r in range(len(current_piece)):
        for c in range(len(current_piece[r])):
            if(current_piece[r][c] == 1):
                x = WIDTH_LEFT + (current_piece_position_x + c) * CELL
                y = (current_piece_position_y + r) * CELL
                rect = pygame.Rect(x,y, CELL, CELL)
                pygame.draw.rect(screen, current_piece_color, rect)
    # Draw board
    for r in range(ROWS):
        for c in range(COLUMNS):
            if BOARD[r][c] != 0:
                rect = pygame.Rect(c*CELL + WIDTH_LEFT,r*CELL,CELL,CELL)
                pygame.draw.rect(screen, PIECE_COLORS[BOARD[r][c]], rect)
    # Draw score
    score_text = font.render(f"SCORE: {int(current_score)}",False, (255,255,255))
    screen.blit(score_text, (5, 160))
    # Draw hold
    hold_text = font.render("HOLD:",False, (255,255,255))
    screen.blit(hold_text, (5,70))
    if hold_piece_index != 0:
        hold_piece = PIECES[hold_piece_index]
        hold_piece_color = PIECE_COLORS[hold_piece_index]
        for r in range(len(hold_piece)):
            for c in range(len(hold_piece[r])):
                if hold_piece[r][c] == 1:
                    x = 5 + c * SMALL_CELL
                    y = 110 + r * SMALL_CELL
                    rect = pygame.Rect(x,y,SMALL_CELL,SMALL_CELL)
                    pygame.draw.rect(screen, hold_piece_color, rect)
    # Draw next piece
    next_text = font.render("NEXT:",False,(255,255,255))
    screen.blit(next_text,(WIDTH_LEFT + WIDTH_BOARD + 15, 70))
    temp = 0
    for i in range(0,4):
        if i<len(current_piece_bag):
            ith_next_piece_index = current_piece_bag[len(current_piece_bag) - i -1]
        else:
            ith_next_piece_index = next_piece_bag[7 - temp - 1]
            temp += 1
        # draw here
        ith_next_piece = PIECES[ith_next_piece_index]
        ith_next_piece_color = PIECE_COLORS[ith_next_piece_index]
        if i == 0:
            size = CELL
            yoffset = 120
            xoffset = 15
        else:
            size = SMALL_CELL
            yoffset = 140 +60 *i
            xoffset = 30
        for r in range(len(ith_next_piece)):
            for c in range(len(ith_next_piece[r])):
                if ith_next_piece[r][c] ==1:
                    x = WIDTH_LEFT + WIDTH_BOARD + xoffset + c*size
                    y = yoffset + r*size
                    rect = pygame.Rect(x,y,size,size)
                    pygame.draw.rect(screen, ith_next_piece_color, rect)
# Update display
    pygame.display.flip()
pygame.quit()
