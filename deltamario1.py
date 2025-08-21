import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Bros")

# Colors
SKY_BLUE = (107, 140, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
GREEN = (0, 168, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 216, 0)
ORANGE = (255, 128, 0)

# Game variables
clock = pygame.time.Clock()
FPS = 60
gravity = 0.5
scroll_threshold = 200
game_over = False
score = 0
font = pygame.font.SysFont('Arial', 24)

# Load images (using simple shapes for this example)
def create_block(size, color):
    surf = pygame.Surface(size)
    surf.fill(color)
    pygame.draw.rect(surf, BLACK, (0, 0, size[0], size[1]), 1)
    return surf

def create_coin():
    surf = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.circle(surf, YELLOW, (6, 6), 6)
    pygame.draw.circle(surf, BLACK, (6, 6), 6, 1)
    return surf

def create_goomba():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    # Body
    pygame.draw.ellipse(surf, (139, 69, 19), (0, 10, 30, 20))
    # Head
    pygame.draw.ellipse(surf, (139, 69, 19), (5, 0, 20, 20))
    # Eyes
    pygame.draw.ellipse(surf, WHITE, (9, 7, 4, 4))
    pygame.draw.ellipse(surf, WHITE, (17, 7, 4, 4))
    pygame.draw.ellipse(surf, BLACK, (10, 8, 2, 2))
    pygame.draw.ellipse(surf, BLACK, (18, 8, 2, 2))
    # Feet
    pygame.draw.ellipse(surf, BLACK, (5, 25, 8, 5))
    pygame.draw.ellipse(surf, BLACK, (17, 25, 8, 5))
    return surf

def create_question_block():
    surf = pygame.Surface((30, 30))
    surf.fill(YELLOW)
    pygame.draw.rect(surf, BLACK, (0, 0, 30, 30), 2)
    pygame.draw.rect(surf, (200, 150, 0), (6, 6, 18, 18))
    pygame.draw.rect(surf, BLACK, (6, 6, 18, 18), 1)
    # Question mark
    pygame.draw.rect(surf, BLACK, (13, 8, 4, 10))
    pygame.draw.rect(surf, BLACK, (10, 18, 10, 4))
    pygame.draw.rect(surf, BLACK, (10, 10, 4, 4))
    return surf

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image.fill(RED)
        pygame.draw.rect(self.image, BLACK, (0, 0, 30, 40), 2)
        # Hat
        pygame.draw.rect(self.image, RED, (0, 5, 30, 10))
        # Face
        pygame.draw.rect(self.image, (255, 182, 193), (5, 15, 5, 5))  # Eye
        pygame.draw.rect(self.image, (255, 182, 193), (20, 15, 5, 5))  # Eye
        pygame.draw.rect(self.image, BLACK, (10, 25, 10, 3))  # Mustache
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True
        self.flip = False

    def update(self, game_over, world_shift):
        if game_over:
            # Game over animation
            self.rect.x += world_shift
            self.rect.y += self.vel_y
            self.vel_y += gravity
            return
        
        dx = 0
        dy = 0

        # Process keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx -= 5
            self.flip = True
        if key[pygame.K_RIGHT]:
            dx += 5
            self.flip = False
        if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
            self.vel_y = -12
            self.jumped = True
        if not key[pygame.K_SPACE]:
            self.jumped = False

        # Add gravity
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Check for collision with ground
        self.in_air = True
        for tile in world.tile_list:
            # Check for collision in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # Check for collision in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if jumping
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                # Check if falling
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        # Check for collision with enemies
        if pygame.sprite.spritecollide(self, enemy_group, False):
            game_over = True

        # Check for collision with coins
        if pygame.sprite.spritecollide(self, coin_group, True):
            global score
            score += 1

        # Check for collision with question blocks
        if pygame.sprite.spritecollide(self, question_block_group, False):
            for block in question_block_group:
                if self.rect.bottom < block.rect.top + 10 and self.vel_y > 0:
                    block.image = create_block((30, 30), ORANGE)
                    # Spawn a coin when hit from below
                    coin = Coin(block.rect.x, block.rect.y - 30)
                    coin_group.add(coin)

        # Update player coordinates
        self.rect.x += dx
        self.rect.y += dy

        # Prevent player from going off the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y = 0
            self.in_air = False

        # Check if player has fallen off the map
        if self.rect.top > HEIGHT:
            game_over = True

        return game_over

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

# World class
class World():
    def __init__(self, data):
        self.tile_list = []
        
        # Load images
        dirt_img = create_block((30, 30), BROWN)
        grass_img = create_block((30, 30), GREEN)
        
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = dirt_img
                    img_rect = img.get_rect()
                    img_rect.x = col_count * 30
                    img_rect.y = row_count * 30
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = grass_img
                    img_rect = img.get_rect()
                    img_rect.x = col_count * 30
                    img_rect.y = row_count * 30
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    enemy = Enemy(col_count * 30, row_count * 30)
                    enemy_group.add(enemy)
                if tile == 4:
                    coin = Coin(col_count * 30, row_count * 30)
                    coin_group.add(coin)
                if tile == 5:
                    q_block = QuestionBlock(col_count * 30, row_count * 30)
                    question_block_group.add(q_block)
                col_count += 1
            row_count += 1
            
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_goomba()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_counter > 50:
            self.move_direction *= -1
            self.move_counter = 0

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_coin()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Question Block class
class QuestionBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_question_block()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Create world
world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Add platforms and enemies
world_data[11][5] = 2
world_data[11][6] = 2
world_data[11][7] = 2
world_data[11][8] = 2
world_data[10][5] = 2
world_data[10][6] = 2
world_data[10][7] = 2
world_data[10][8] = 2

world_data[9][10] = 2
world_data[9][11] = 2
world_data[9][12] = 2
world_data[8][10] = 2
world_data[8][11] = 2
world_data[8][12] = 2

world_data[7][15] = 2
world_data[7][16] = 2
world_data[7][17] = 2
world_data[6][15] = 2
world_data[6][16] = 2
world_data[6][17] = 2

world_data[10][3] = 3  # Enemy
world_data[9][14] = 3  # Enemy

world_data[8][5] = 4  # Coin
world_data[7][10] = 4  # Coin
world_data[6][15] = 4  # Coin

world_data[7][5] = 5  # Question block
world_data[6][10] = 5  # Question block

player = Player(100, HEIGHT - 130)
enemy_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
question_block_group = pygame.sprite.Group()

world = World(world_data)

# Game loop
running = True
while running:
    clock.tick(FPS)
    
    # Draw background
    screen.fill(SKY_BLUE)
    
    # Draw world
    world.draw()
    
    # Draw groups
    enemy_group.draw(screen)
    coin_group.draw(screen)
    question_block_group.draw(screen)
    
    # Draw player
    player.draw()
    
    # Update groups
    if not game_over:
        enemy_group.update()
    
    # Update player
    game_over = player.update(game_over, 0)
    
    # Draw score
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Game over text
    if game_over:
        game_over_text = font.render('Game Over! Press R to restart', True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # Reset game
                player = Player(100, HEIGHT - 130)
                enemy_group.empty()
                coin_group.empty()
                question_block_group.empty()
                world = World(world_data)
                game_over = False
                score = 0
    
    pygame.display.update()

pygame.quit()
