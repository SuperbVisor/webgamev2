import pygame
import random
import os
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy

# initiallize pygame
mixer.init()
pygame.init()

# game window
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Jumpy Game')
icon = pygame.image.load('Game1/assets/ghost.png')
pygame.display.set_icon(icon)

# set frame rate
clock = pygame.time.Clock()
FPS = 60

# load music and sounds
pygame.mixer.music.load('Game1/assets/fuyu-biyori bgm.mp3')
pygame.mixer.music.set_volume(0.9)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound('Game1/assets/jump.mp3')
jump_fx.set_volume(1)
death_fx = pygame.mixer.Sound('Game1/assets/death.mp3')
death_fx.set_volume(1)

# game variable
SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else: 
    high_score = 0

# colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# PANEL = (153, 217, 234) ga jadi

# font
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)

# load images
jumpy_image = pygame.image.load('Game1/assets/bocchi1.png').convert_alpha()
bg_image = pygame.image.load('Game1/assets/background2.png').convert_alpha()
platform_image = pygame.image.load('Game1/assets/wood.png').convert_alpha()

# bird spritesheet
bird_sheet_img = pygame.image.load('Game1/assets/bird.png').convert_alpha()
bird_sheet = SpriteSheet(bird_sheet_img)

# function for displaying text to the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# draw panel info
def draw_panel():
    # pygame.draw.line(screen, WHITE, (0, 30), (SCREEN_WIDTH, 30), 2) ga jadi pake ini
    draw_text('SCORE: ' + str(score), font_small, WHITE, 0, 0)

# function for drawing bg
def draw_bg(bg_scroll):
    screen.blit(bg_image, (0, 0 + bg_scroll))
    screen.blit(bg_image, (0, -600 + bg_scroll))

# player class
class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(jumpy_image, (45, 45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False
    
    def move(self):
        # reset variable
        scroll = 0
        dx = 0
        dy = 0
        
        # process key presses
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx = -10
            self.flip = False
        if key[pygame.K_d]:
            dx = 10
            self.flip = True
        
        # gravity
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        # screen limit for player
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        # check collosion with platforms
        for platform in platform_group:
            # collosion in y direction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # chech if above platform
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20
                        jump_fx.play()

        # check if player has bounced to the top of the screen
        if self.rect.top <= SCROLL_THRESH:
            # if player is jumping
            if self.vel_y < 0:
                scroll = -dy

        # update rect position
        self.rect.x += dx
        self.rect.y += dy + scroll

        # update mask
        self.mask = pygame.mask.from_surface(self.image)

        return scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))   # buat ngeflip gambar sesuai arah move


# platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self,x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        # moving platform side to side
        if self.moving == True:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed
        
        # change platform direction if it has moved fully or hit a wall
        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1
            self.move_counter = 0
        
        # update vertical position
        self.rect.y += scroll

        # check if platform has gone off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# player instance
jumpy = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

# create sprite groups
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# create starting platforms
platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
platform_group.add(platform)

# game loop
run = True
while run:
    
    clock.tick(FPS)
    
    if game_over == False:
        scroll = jumpy.move()

        # draw bg
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        # generate platform
        if len(platform_group) < MAX_PLATFORMS:
            p_w = random.randint(40,60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 1000:
                p_moving = True
            else:
                p_moving = False
            platform = Platform(p_x, p_y, p_w, p_moving)
            platform_group.add(platform)

        # update platform
        platform_group.update(scroll)

        # generate enemies
        if len(enemy_group) == 0 and score > 2000:
            enemy = Enemy(SCREEN_WIDTH, 100, bird_sheet, 1.5)
            enemy_group.add(enemy)
        
        # update enemies
        enemy_group.update(scroll, SCREEN_WIDTH)

        # update score
        if scroll > 0:
            score += scroll

        # draw line at previous high score
        pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
        draw_text('HIGH SCORE', font_small, WHITE, SCREEN_WIDTH -130, score - high_score + SCROLL_THRESH)

        # draw sprites
        platform_group.draw(screen)
        enemy_group.draw(screen)
        jumpy.draw()
        
        # draw panel
        draw_panel()

        # check game over
        if jumpy.rect.top > SCREEN_HEIGHT:
            game_over = True
            death_fx.play()
        
        # check for collosion with enemy
        if pygame.sprite.spritecollide(jumpy, enemy_group, False):
            if pygame.sprite.spritecollide(jumpy, enemy_group, False, pygame.sprite.collide_mask):
                game_over = True
                death_fx.play()
    
    else:
        if fade_counter < SCREEN_WIDTH:
            fade_counter += 5
            for y in range(0, 6, 2):
                pygame.draw.rect(screen, BLACK, (0, y * 100, fade_counter, 100))
                pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * 100, SCREEN_WIDTH, 100))
        else:
            draw_text('GAME OVER!', font_big, WHITE, 130, 200)
            draw_text('SCORE: ' + str(score), font_big, WHITE, 130, 250)
            draw_text('PRESS SPACE TO PLAY AGAIN', font_big, WHITE, 40, 300)
            # update high score
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                # reset variable
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                # reposition player
                jumpy.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
                # reset enemies
                enemy_group.empty()
                # reset platforms
                platform_group.empty()
                # create starting platform
                platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
                platform_group.add(platform)

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # update high score
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            run = False
    
    # update display
    pygame.display.update()

pygame.quit()