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
BOARD = [[0 for i in range(COLUMNS)] for i in range(ROWS)]      #10x20 grid, initial value = 0 means empty board.
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
GHOST_COLOR = (153, 153, 153)
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
# SRS Kick table
JLSTZ_KICKS = {
    (0,1): [(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
    (1,0): [(0,0),(1,0),(1,-1),(0,2),(1,2)],

    (1,2): [(0,0),(1,0),(1,-1),(0,2),(1,2)],
    (2,1): [(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],

    (2,3): [(0,0),(1,0),(1,1),(0,-2),(1,-2)],
    (3,2): [(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],

    (3,0): [(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
    (0,3): [(0,0),(1,0),(1,1),(0,-2),(1,-2)]
}
I_KICKS = {
    (0,1): [(0,0),(-2,0),(1,0),(-2,-1),(1,2)],
    (1,0): [(0,0),(2,0),(-1,0),(2,1),(-1,-2)],

    (1,2): [(0,0),(-1,0),(2,0),(-1,2),(2,-1)],
    (2,1): [(0,0),(1,0),(-2,0),(1,-2),(-2,1)],          

    (2,3): [(0,0),(2,0),(-1,0),(2,1),(-1,-2)],
    (3,2): [(0,0),(-2,0),(1,0),(-2,-1),(1,2)],

    (3,0): [(0,0),(1,0),(-2,0),(1,-2),(-2,1)],
    (0,3): [(0,0),(-1,0),(2,0),(-1,2),(2,-1)]
}
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
def rotate(piece,clockwise = True):
    global lock_timer
    lock_timer = 0
    if clockwise == True:
        return [list(row)[::-1] for row in zip(*piece)]
    else:
        return [list(row) for row in zip(*piece)][::-1]
def try_rotate(current_piece, pos_x, pos_y, clockwise):  # Trying every possible wall kicks until the first valid one
    global current_rotation, current_piece_index
    new_rotation = (current_rotation + (1 if clockwise else -1)) % 4    
    rotated_piece = rotate(current_piece, clockwise)
    kick_table = []
    if current_piece_index == 1:    # I piece
        kick_table = I_KICKS
    else:
        kick_table = JLSTZ_KICKS
    for dx,dy in kick_table[(current_rotation,new_rotation)]:
        if not check_collision(rotated_piece, pos_x + dx, pos_y + dy):
            return rotated_piece, pos_x + dx, pos_y + dy
    return current_piece, pos_x, pos_y
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
    global current_piece_bag, next_piece_bag, canHold, fall_timer, lock_reset_counter, touched_floor, game_state
    touched_floor = False
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
        game_state = 2
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
def reset():
    global BOARD, current_piece_index,current_piece_color,current_piece,current_piece_position_x,current_piece_position_y
    global fall_timer,fall_delay,fall_delay_temp,total_line_cleared,level,touched_floor,choice, current_rotation
    global time_hold,move_timer,move_direction,lock_timer,lock_reset_counter,current_score,current_piece_bag,next_piece_bag,isHolding,hold_piece_index,canHold
    choice = 0
    BOARD = [[0 for i in range(COLUMNS)] for i in range(ROWS)]

    fall_timer = 0
    fall_delay = 800
    fall_delay_temp = 0         
    touched_floor = False

    time_hold = 0
    move_timer = 0
    move_direction = 0

    lock_timer = 0
    lock_reset_counter = 0

    current_score = 0
    level = 0
    total_line_cleared = 0

    current_rotation = 0

    current_piece_bag = list(range(1,8))
    random.shuffle(current_piece_bag)
    next_piece_bag = list(range(1,8))
    random.shuffle(next_piece_bag)

    current_piece_index = current_piece_bag.pop()
    current_piece_color = PIECE_COLORS[current_piece_index]
    current_piece = PIECES[current_piece_index]
    current_piece_position_x = COLUMNS//2 - len(current_piece[0])//2
    current_piece_position_y = 0

    isHolding = False
    hold_piece_index = 0
    canHold = True
# Initialize Pygame
screen = pygame.display.set_mode((WIDTH_BOARD+WIDTH_LEFT+WIDTH_RIGHT,HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font("assets/font/Ithaca-LVB75.ttf",size = 32)
font_big = pygame.font.Font("assets/font/Ithaca-LVB75.ttf",size = 45)
main_UI = pygame.image.load("assets/UI/Main_UI.png")
logo = pygame.image.load("assets/UI/tetris_logo.png")
running = True
# Initialize current piece before game starts
fall_timer = 0
fall_delay = 800            # Time between each fall
soft_drop_multiplier = 10   # Speed increase when holding softdrop button
fall_delay_temp = 0         # Used to store the current fall delay before pressing softdrop button
total_line_cleared = 0
level = 0
current_score = 0

time_hold = 0
slide_delay = 200       # Starts sliding after holding for 200ms

move_timer = 0
move_delay = 100        # Slide every 100ms
move_direction = 0

lock_delay = 500        # lock into board after 500ms
lock_timer = 0

max_lock_reset = 15     # Number of actions the player can perform once they touch the ground
lock_reset_counter = 0  # Once the player touches the ground, each movement/rotation counts as an action
touched_floor = False

current_piece_bag = list(range(1,8))    # 2 Bags, one is used for block prediction
random.shuffle(current_piece_bag)
next_piece_bag = list(range(1,8))
random.shuffle(next_piece_bag)

current_piece_index = current_piece_bag.pop()
current_piece_color = PIECE_COLORS[current_piece_index]
current_piece = PIECES[current_piece_index]
current_piece_position_x = COLUMNS//2 - len(current_piece[0])//2    # Spawn centering
current_piece_position_y = 0

isHolding = False
hold_piece_index = 0
canHold = True
current_rotation = 0    #used for SRS Kick tables. 0-default, 1-90°, 2-180°, 3-270° (clock wise rotation) 
# Game states: 
# 0-title screen
# 1-game screen
# 2-ending screen
game_state = 0
choice = 0
while running:
    dt = clock.tick(60)     #limit to 60fps
###########################################################################
##############################TITLE SCREEN#################################
###########################################################################
    if game_state == 0:
        start_text = font_big.render("START",False,(255,255,255))           #choice = 0
        start_selected_text = font_big.render("START",False,(255,255,102))
        quit_text = font_big.render("QUIT",False,(255,255,255))             #choice = 1
        quit_selected_text = font_big.render("QUIT",False,(255,255,102))
        # Logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    choice = 1-choice
                elif event.key == pygame.K_UP:
                    choice = 1-choice
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    if choice == 0:
                        game_state = 1
                    if choice == 1:
                        running = False     
        # Draw
        screen.fill((0,0,0))
        screen.blit(logo,(0,0))
        if choice == 0:
            screen.blit(start_selected_text,(260, 300))
            screen.blit(quit_text,(260,350))
        else:
            screen.blit(start_text,(260, 300))
            screen.blit(quit_selected_text,(260,350))
###########################################################################
###############################GAME SCREEN#################################
###########################################################################
    if game_state == 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Move left/right
                if event.key == pygame.K_LEFT and not check_collision(current_piece,current_piece_position_x-1,current_piece_position_y):
                    if lock_reset_counter < 15 and touched_floor:
                        lock_timer = 0
                        lock_reset_counter += 1
                    current_piece_position_x -= 1
                    move_direction = -1
                    move_timer = 0
                elif event.key == pygame.K_RIGHT and not check_collision(current_piece,current_piece_position_x+1, current_piece_position_y):
                    if lock_reset_counter < 15 and touched_floor:
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
                    if lock_reset_counter < 15:
                        if touched_floor:
                            lock_timer = 0
                            lock_reset_counter += 1
                        current_piece, current_piece_position_x, current_piece_position_y = try_rotate(current_piece, current_piece_position_x, current_piece_position_y, True)
                        current_rotation = (current_rotation+1)%4
                elif event.key == pygame.K_z:
                    if lock_reset_counter < 15: 
                        if touched_floor:
                            lock_timer = 0
                            lock_reset_counter += 1
                        current_piece, current_piece_position_x, current_piece_position_y = try_rotate(current_piece, current_piece_position_x, current_piece_position_y, False)
                        current_rotation = (current_rotation-1) % 4
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
                    if lock_reset_counter < 15 and touched_floor:
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
            touched_floor = True
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
        # Draw score
        score_text = font.render(f"SCORE: {int(current_score)}",False, (255,255,255))
        screen.blit(score_text, (5, 160))
        # Draw level
        level_text = font.render(f"LEVEL: {int(level)}",False,(255,255,255))
        screen.blit(level_text,(5,250))
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
###########################################################################
##############################ENDING SCREEN################################
###########################################################################
    if game_state == 2:
        retry_text = font_big.render("RETRY",False,(255,255,255))              #choice = 0
        retry_selected_text = font_big.render("RETRY",False,(255,255,102))
        quit_text = font_big.render("QUIT",False,(255,255,255))                 #choice = 1
        quit_selected_text = font_big.render("QUIT",False,(255,255,102))
        score_text = font_big.render(f"SCORE: {int(current_score)}",False,(255,255,255))
        # Logic
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    choice = 1-choice
                elif event.key == pygame.K_UP:
                    choice = 1-choice
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    if choice == 0:
                        game_state = 1
                        reset()
                    if choice == 1:
                        running = False     
        # Draw
        screen.fill((0,0,0))
        screen.blit(score_text, (260,230))
        if choice == 0:
            screen.blit(retry_selected_text,(260, 300))
            screen.blit(quit_text,(260,350))
        else:
            screen.blit(retry_text,(260, 300))
            screen.blit(quit_selected_text,(260,350))    
# Update display
    pygame.display.flip()
pygame.quit()
