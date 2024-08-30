import copy
import pygame
import math
from constants import WIDTH, HEIGHT, FPS, map, SPAWN_TILE, THRESHOLD, PI, IMAGE_SCALE

pygame.init()

# Set game resolution and window name
game_window = pygame.display.set_mode([900, 970])
pygame.display.set_caption("Pac-Man")

# Game clock
timer = pygame.time.Clock()
font = pygame.font.Font('PacFont.ttf', 30)
level = copy.deepcopy(map)
color = 'lightcoral'
pac_icon = []
pac_cherry_icon = []

# Load images
for i in range(1, 10):
    pac_icon.append(pygame.transform.scale(pygame.image.load(f'pacman/{i}.png'), IMAGE_SCALE))
    pac_cherry_icon.append(pygame.transform.scale(pygame.image.load(f'pacman_cherry/{i}.png'), IMAGE_SCALE))

blinky_img = pygame.transform.scale(pygame.image.load(f'ghosts/red.png'), IMAGE_SCALE)
spooked_img = pygame.transform.scale(pygame.image.load(f'ghosts/cherry.png'), IMAGE_SCALE)
dead_img = pygame.transform.scale(pygame.image.load(f'ghosts/dead.png'), IMAGE_SCALE)
# Game variables
pac_x = 450
pac_y = 663
direction = 0
blinky_x = 440
blinky_y = 438
blinky_direction = 2
counter = 0
shine = False
valid_moves = [False, False, False, False]
direction_temp = 0
pac_vel = 2
score = 0
cherry = False
cherry_timer = 0
ghost_isEaten = [False]
destination = [(pac_x, pac_y)]
red_isDead = False
red_inSpawn = False
start = False
ghost_vel = [2]
invuln = 0
lives = 3
game_over = False
game_won = False
animation_speed = 5 
animation_direction = -1


class Ghost:
    def __init__(self, x_pos, y_pos, destination, ghost_vel, sprite, direction, dead, spawn, queue):
        self.x_pos, self.y_pos = x_pos, y_pos
        self.center_x, self.center_y = x_pos + 22, y_pos + 22
        self.destination, self.ghost_vel, self.sprite, self.direction, self.dead, self.in_spawn, self.queue = (
            destination,
            ghost_vel,
            sprite,
            direction,
            dead,
            spawn,
            queue,
        )
        self.turns, self.in_spawn = self.pac_collide()
        self.rect = self.draw()


    def draw(self):
        if (not cherry and not self.dead) or (ghost_isEaten[self.queue] and cherry and not self.dead):
            game_window.blit(self.sprite, (self.x_pos, self.y_pos))
        elif cherry and not self.dead and not ghost_isEaten[self.queue]:
            game_window.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            game_window.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect

    def pac_collide(self):
        # Dimensions of the Pac-Man bounding box
        pacman_radius = 180  # As defined in the image generation code
        pacman_diameter = pacman_radius * 2
        pacman_x_left = self.center_x - pacman_radius
        pacman_x_right = self.center_x + pacman_radius
        pacman_y_top = self.center_y - pacman_radius
        pacman_y_bottom = self.center_y + pacman_radius

        d_Height = ((HEIGHT - 50) // 32)
        d_Width = (WIDTH // 30)
        self.turns = [False, False, False, False]

        # Check the walls around Pac-Man's bounding box
        if 0 < self.center_x // 30 < 29:
            # Check up
            if level[(self.center_y - THRESHOLD) // d_Height][self.center_x // d_Width] == 9:
                self.turns[2] = True
            if level[self.center_y // d_Height][self.center_x // d_Width] < 3 or \
            (level[self.center_y // d_Height][self.center_x // d_Width] == 9 and (self.in_spawn or self.dead)):
                self.turns[1] = True
            if level[self.center_y // d_Height][(self.center_x + THRESHOLD) // d_Width] < 3 or \
            (level[self.center_y // d_Height][(self.center_x + THRESHOLD) // d_Width] == 9 and (self.in_spawn or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + THRESHOLD) // d_Height][self.center_x // d_Width] < 3 or \
            (level[(self.center_y + THRESHOLD) // d_Height][self.center_x // d_Width] == 9 and (self.in_spawn or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - THRESHOLD) // d_Height][self.center_x // d_Width] < 3 or \
            (level[(self.center_y - THRESHOLD) // d_Height][self.center_x // d_Width] == 9 and (self.in_spawn or self.dead)):
                self.turns[2] = True

            # Check boundaries based on current direction
            if self.direction in [2, 3]:  # Moving up or down
                if 12 <= self.center_x % d_Width <= 18:
                    if level[(self.center_y + THRESHOLD) // d_Height][self.center_x // d_Width] < 3 or \
                    (level[(self.center_y + THRESHOLD) // d_Height][self.center_x // d_Width] == 9 and (self.in_spawn or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - THRESHOLD) // d_Height][self.center_x // d_Width] < 3 or \
                    (level[(self.center_y - THRESHOLD) // d_Height][self.center_x // d_Width] == 9 and (self.in_spawn or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % d_Height <= 18:
                    if level[self.center_y // d_Height][(self.center_x - d_Width) // d_Width] < 3 or \
                    (level[self.center_y // d_Height][(self.center_x - d_Width) // d_Width] == 9 and (self.in_spawn or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // d_Height][(self.center_x + d_Width) // d_Width] < 3 or \
                    (level[self.center_y // d_Height][(self.center_x + d_Width) // d_Width] == 9 and (self.in_spawn or self.dead)):
                        self.turns[0] = True

            if self.direction in [0, 1]:  # Moving left or right
                if 12 <= self.center_x % d_Width <= 18:
                    if level[(self.center_y + THRESHOLD) // d_Height][self.center_x // d_Width] < 3 or \
                    (level[(self.center_y + THRESHOLD) // d_Height][self.center_x // d_Width] == 9 and (self.in_spawn or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - THRESHOLD) // d_Height][self.center_x // d_Width] < 3 or \
                    (level[(self.center_y - THRESHOLD) // d_Height][self.center_x // d_Width] == 9 and (self.in_spawn or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % d_Height <= 18:
                    if level[self.center_y // d_Height][(self.center_x - THRESHOLD) // d_Width] < 3 or \
                    (level[self.center_y // d_Height][(self.center_x - THRESHOLD) // d_Width] == 9 and (self.in_spawn or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // d_Height][(self.center_x + THRESHOLD) // d_Width] < 3 or \
                    (level[self.center_y // d_Height][(self.center_x + THRESHOLD) // d_Width] == 9 and (self.in_spawn or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True

        # Check spawn area
        if 350 < self.center_x < 550 and 370 < self.center_y < 480:
            self.in_spawn = True
        else:
            self.in_spawn = False

        return self.turns, self.in_spawn

    def move_red(self):
        if self.direction == 0:
            if self.destination[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.ghost_vel
            elif not self.turns[0]:
                if self.destination[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.ghost_vel
                elif self.destination[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.ghost_vel
                elif self.destination[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.ghost_vel
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.ghost_vel
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.ghost_vel
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.ghost_vel
            elif self.turns[0]:
                if self.destination[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.ghost_vel
                if self.destination[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.ghost_vel
                else:
                    self.x_pos += self.ghost_vel
        elif self.direction == 1:
            if self.destination[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.destination[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.ghost_vel
            elif not self.turns[1]:
                if self.destination[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.ghost_vel
                elif self.destination[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.ghost_vel
                elif self.destination[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.ghost_vel
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.ghost_vel
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.ghost_vel
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.ghost_vel
            elif self.turns[1]:
                if self.destination[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.ghost_vel
                if self.destination[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.ghost_vel
                else:
                    self.x_pos -= self.ghost_vel
        elif self.direction == 2:
            if self.destination[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.ghost_vel
            elif self.destination[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.ghost_vel
            elif not self.turns[2]:
                if self.destination[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.ghost_vel
                elif self.destination[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.ghost_vel
                elif self.destination[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.ghost_vel
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.ghost_vel
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.ghost_vel
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.ghost_vel
            elif self.turns[2]:
                if self.destination[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.ghost_vel
                elif self.destination[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.ghost_vel
                else:
                    self.y_pos -= self.ghost_vel
        elif self.direction == 3:
            if self.destination[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.ghost_vel
            elif not self.turns[3]:
                if self.destination[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.ghost_vel
                elif self.destination[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.ghost_vel
                elif self.destination[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.ghost_vel
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.ghost_vel
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.ghost_vel
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.ghost_vel
            elif self.turns[3]:
                if self.destination[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.ghost_vel
                elif self.destination[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.ghost_vel
                else:
                    self.y_pos += self.ghost_vel
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction



def scoreboard():
    global game_over, game_won  # Ensure you can access these variables
    
    # Display current score
    score_text = font.render(f'{score}', True, 'lightgreen')
    game_window.blit(score_text, (10, 920))
    
    # Display lives
    game_window.blit(font.render("Lives: "f'{lives}', True, 'lightgreen'), (790, 920))
    
    # Display Level
    game_window.blit(font.render("Level 1", True, 'lightcoral'), (420 , 920))
    
    # Display end game screen with total score and colored border
    if game_over or game_won:
        # Determine border color and message based on the game outcome
        border_color = 'red' if game_over else 'green'
        message = 'YOU DIED' if game_over else 'GAME WON!'
        gameover_text = font.render(f'{message} - Score: {score}', True, border_color)
        
        # Draw background
        background_rect = pygame.Rect(200, 400, 400, 200)
        pygame.draw.rect(game_window, 'black', background_rect, 0, 10)
        
        # Draw border
        border_rect = background_rect.inflate(10, 10)  # Inflate the background rectangle to draw the border
        pygame.draw.rect(game_window, border_color, border_rect, 5, 10)  # Border width set to 5, adjust position and size if needed
        
        # Calculate text position to center it
        text_rect = gameover_text.get_rect(center=background_rect.center)
        
        # Draw game over message
        game_window.blit(gameover_text, text_rect.topleft)


def eat_pucks(score, cherry, cherry_timer, ghost_isEaten):
    d_Height = (HEIGHT - 50) // 32
    d_Width = WIDTH // 30
    if 0 < pac_x < 870:
        if map[center_y // d_Height][center_x // d_Width] == 1:
            map[center_y // d_Height][center_x // d_Width] = 0
            score += 10
        if map[center_y // d_Height][center_x // d_Width] == 2:
            map[center_y // d_Height][center_x // d_Width] = 0
            score += 50
            cherry = True
            cherry_timer = 0
            ghost_isEaten = [False]
    return score, cherry, cherry_timer, ghost_isEaten


def board_spawn():
    d_Height = (HEIGHT - 50) // 32
    d_Width = WIDTH // 30
    wall_thickness = 30 # Thickness of the lines you used earlier

    for i, row in enumerate(map):
        for j, cell in enumerate(row):
            rect = pygame.Rect(j * d_Width, i * d_Height, d_Width, d_Height)
            center_x = (j + 0.5) * d_Width
            center_y = (i + 0.5) * d_Height

            if cell == 1:
                pygame.draw.circle(game_window, 'white', (center_x, center_y), 3)
            elif cell == 2 and not shine:
                pygame.draw.circle(game_window, 'orange', (center_x, center_y), 9)
            elif cell == 3:  # Draw a vertical wall block
                pygame.draw.rect(game_window, color, pygame.Rect(j * d_Width, i * d_Height + (d_Height - wall_thickness) // 2, d_Width, wall_thickness))
            elif cell == 4:  # Draw a horizontal wall block
                pygame.draw.rect(game_window, color, pygame.Rect(j * d_Width + (d_Width - wall_thickness) // 2, i * d_Height, wall_thickness, d_Height))
            elif cell in [5, 6, 7, 8]:  # Draw solid wall block with shading
                pygame.draw.rect(game_window, color, rect)
                # Draw solid red block as shading for thick walls
                pygame.draw.rect(game_window, 'red', pygame.Rect(j * d_Width + wall_thickness // 2, i * d_Height + wall_thickness // 2, d_Width - wall_thickness, d_Height - wall_thickness))


def update_counter():
    global counter, animation_direction

    # Update counter based on animation direction
    counter += animation_direction
    
    # Smoothly reverse direction and cap counter
    if counter >= 90:
        animation_direction = -1
        counter = 90
    elif counter <= 0:
        animation_direction = 1
        counter = 0

def player_spawn():
    global counter, animation_direction

    # Determine which icon to use based on the cherry state
    icon = pac_cherry_icon if cherry else pac_icon
    
    # Calculate the index of the image to use
    icon_index = (counter // animation_speed) % 9  # 9 images
    
    # Update counter based on animation direction
    counter += animation_direction
    if counter >= 90:  # Total frames for bidirectional animation
        animation_direction = -1  # Reverse direction
        counter = 90  # Cap counter to avoid going below 0
    elif counter <= 0:
        animation_direction = 1  # Forward direction
        counter = 0  # Reset counter to avoid exceeding maximum

    # Rotate icon based on direction
    if direction == 0:
        rotated_icon = icon[icon_index]
    elif direction == 1:
        rotated_icon = pygame.transform.rotate(icon[icon_index], 180)
    elif direction == 2:
        rotated_icon = pygame.transform.rotate(icon[icon_index], 90)
    elif direction == 3:
        rotated_icon = pygame.transform.rotate(icon[icon_index], -90)

    # Draw the icon
    game_window.blit(rotated_icon, (pac_x, pac_y))




def get_location(centerx, centery):
    turns = [False, False, False, False]
    d_Height = (HEIGHT - 50) // 32
    d_Width = (WIDTH // 30)
    
    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // d_Height][(centerx - THRESHOLD) // d_Width] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // d_Height][(centerx + THRESHOLD) // d_Width] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + THRESHOLD) // d_Height][centerx // d_Width] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - THRESHOLD) // d_Height][centerx // d_Width] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 12 <= centerx % d_Width <= 18:
                if level[(centery + THRESHOLD) // d_Height][centerx // d_Width] < 3:
                    turns[3] = True
                if level[(centery - THRESHOLD) // d_Height][centerx // d_Width] < 3:
                    turns[2] = True
            if 12 <= centery % d_Height <= 18:
                if level[centery // d_Height][(centerx - d_Width) // d_Width] < 3:
                    turns[1] = True
                if level[centery // d_Height][(centerx + d_Width) // d_Width] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 12 <= centerx % d_Width <= 18:
                if level[(centery + d_Height) // d_Height][centerx // d_Width] < 3:
                    turns[3] = True
                if level[(centery - d_Height) // d_Height][centerx // d_Width] < 3:
                    turns[2] = True
            if 12 <= centery % d_Height <= 18:
                if level[centery // d_Height][(centerx - THRESHOLD) // d_Width] < 3:
                    turns[1] = True
                if level[centery // d_Height][(centerx + THRESHOLD) // d_Width] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True

    return turns


def pac_controls(move_X, move_Y):
    direction_to_coords = {0: (pac_vel, 0), 1: (-pac_vel,0), 2: (0, -pac_vel), 3: (0, pac_vel)}

    if valid_moves[direction]:
        dx, dy = direction_to_coords.get(direction, (0, 0))
        move_X += dx
        move_Y += dy

    return move_X, move_Y


def get_destination(red_ghost_x, red_ghost_y):
    if pac_x < 450:
        escape_h = 900
    else:
        escape_h = 0
    if pac_y < 450:
        escape_v = 900
    else:
        escape_v = 0
    return_destination = (380, 400)
    if cherry:
        if not Blinky.dead and not ghost_isEaten[0]:
            red_ghost_dest = (450, 450)
        elif not Blinky.dead and ghost_isEaten[0]:
            if 340 < red_ghost_x < 560 and 340 < red_ghost_y < 500:
                red_ghost_dest = (400, 100)
            else:
                red_ghost_dest = (pac_x, pac_y)
        else:
            red_ghost_dest = return_destination
    else:
        if not Blinky.dead:
            if 340 < red_ghost_x < 560 and 340 < red_ghost_y < 500:
                red_ghost_dest = (400, 100)
            else:
                red_ghost_dest = (pac_x, pac_y)
        else:
            red_ghost_dest = return_destination
    return [red_ghost_dest]


flag = True
while flag:
    timer.tick(FPS)
    
    # Update animation state
    update_counter()

    # Handle shine state
    if counter > 10:  # Adjust this threshold based on animation speed
        shine = False
    else:
        shine = True

    # Handle cherry timer
    if cherry and cherry_timer < 450:
        cherry_timer += 1
    elif cherry and cherry_timer >= 450:
        cherry_timer = 0
        cherry = False
        ghost_isEaten = [False]

    # Handle invulnerability timer
    if invuln < 180 and not game_over and not game_won:
        start = False
        invuln += 1
    else:
        start = True

    game_window.fill('black')
    board_spawn()
    center_x = pac_x + 23
    center_y = pac_y + 24
    if cherry:
        ghost_vel = [1]
    else:
        ghost_vel = [2]
    if ghost_isEaten[0]:
        ghost_vel[0] = 2
    if red_isDead:
        ghost_vel[0] = 4

    game_won = True
    for i in range(len(map)):
        if 1 in map[i] or 2 in map[i]:
            game_won = False

    player_circle = pygame.draw.circle(game_window, 'black', (center_x, center_y), 20, 2)
    player_spawn()
    Blinky = Ghost(blinky_x, blinky_y, destination[0], ghost_vel[0], blinky_img, blinky_direction, red_isDead,
                  red_inSpawn, 0)
    scoreboard()
    destination = get_destination(blinky_x, blinky_y)

    valid_moves = get_location(center_x, center_y)
    if start:
        pac_x, pac_y = pac_controls(pac_x, pac_y)
        blinky_x, blinky_y, blinky_direction = Blinky.move_red()
    score, cherry, cherry_timer, ghost_isEaten = eat_pucks(score, cherry, cherry_timer, ghost_isEaten)

    if not cherry:
        if (player_circle.colliderect(Blinky.rect) and not Blinky.dead):
            if lives > 0:
                lives -= 1
                invuln = 0
                cherry = False
                cherry_timer = 0
                pac_x = 450
                pac_y = 663
                direction = 0
                direction_temp = 0
                blinky_x = 440
                blinky_y = 438
                blinky_direction = 2
                ghost_isEaten = [False, False, False, False]
                red_isDead = False
            else:
                game_over = True
                start = False
                invuln = 0
    if cherry and player_circle.colliderect(Blinky.rect) and ghost_isEaten[0] and not Blinky.dead:
        if lives > 0:
            cherry = False
            cherry_timer = 0
            lives -= 1
            invuln = 0
            pac_x = 450
            pac_y = 663
            direction = 0
            direction_temp = 0
            blinky_x = 440
            blinky_y = 438
            blinky_direction = 2
            ghost_isEaten = [False, False, False, False]
            red_isDead = False
        else:
            game_over = True
            start = False
            invuln = 0
    if cherry and player_circle.colliderect(Blinky.rect) and not Blinky.dead and not ghost_isEaten[0]:
        red_isDead = True
        ghost_isEaten[0] = True
        score += (ghost_isEaten.count(True)) * 200

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_temp= 0
            if event.key == pygame.K_LEFT:
                direction_temp= 1
            if event.key == pygame.K_UP:
                direction_temp = 2
            if event.key == pygame.K_DOWN:
                direction_temp = 3
            if event.key == pygame.K_SPACE and (game_over or game_won):
                cherry = False
                cherry_timer = 0
                lives -= 1
                invuln = 0
                pac_x = 450
                pac_y = 663
                direction = 0
                blinky_x = 440
                blinky_y = 438
                blinky_direction = 2
                ghost_isEaten = [False]
                red_isDead = False
                score = 0
                lives = 3
                map = copy.deepcopy(level)
                game_over = False
                game_won = False
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_temp == 0:
                direction_temp = direction
            if event.key == pygame.K_LEFT and direction_temp == 1:
                direction_temp = direction
            if event.key == pygame.K_UP and direction_temp == 2:
                direction_temp = direction
            if event.key == pygame.K_DOWN and direction_temp == 3:
                direction_temp = direction

    if direction_temp == 0 and valid_moves[0]:
        direction = 0
    if direction_temp == 1 and valid_moves[1]:
        direction = 1
    if direction_temp == 2 and valid_moves[2]:
        direction = 2
    if direction_temp == 3 and valid_moves[3]:
        direction = 3    

    if pac_x > 900:
        pac_x = -47
    elif pac_x < -50:
        pac_x = 897

    if Blinky.in_spawn and red_isDead:
        red_isDead = False

    pygame.display.flip()
pygame.quit()