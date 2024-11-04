import pygame
import random

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)

class Alien(pygame.sprite.Sprite):
    def __init__(self, image_path, is_bomb_block=False, scale_size=(40, 30)):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, scale_size)  
        self.rect = self.image.get_rect()
        self.is_bomb_block = is_bomb_block

class Barrier(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(GREY)
        self.rect = self.image.get_rect()

class Player(pygame.sprite.Sprite):
    def __init__(self, image_path, scale_size=(20, 20)):
        super().__init__()
        self.image = pygame.image.load(image_path)  
        self.image = pygame.transform.scale(self.image, scale_size)
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        self.rect.x = (600 - self.rect.width) // 2
        self.rect.y = 670

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.x < 580:
            self.rect.x += 5

class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([4, 10])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y -= 5

class Bomb(pygame.sprite.Sprite):
    def __init__(self, image_path, scale_size=(16, 16)):
        super().__init__()
        self.image = pygame.image.load(image_path) 
        self.image = pygame.transform.scale(self.image, scale_size)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y += 3

class BlockBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([4, 10])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.y += 5

pygame.init()

screen_width = 600
screen_height = 700
screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption("Space Invaders Clone")

all_sprites_list = pygame.sprite.Group()
alien_list = pygame.sprite.Group()
barrier_list = pygame.sprite.Group()
bullet_list = pygame.sprite.Group()
bomb_list = pygame.sprite.Group()
block_bullet_list = pygame.sprite.Group()

def reset_game():
    global score, player, done, block_speed, lives
    score = 0
    lives = 3
    done = False
    block_speed = 1
    
    for group in (alien_list, barrier_list, bullet_list, bomb_list, block_bullet_list):
        group.empty()

    for j in range(5):
        for i in range(10):
            is_bomb_block = (j < 2 and i < 10)
            alien = Alien('Alien.png', is_bomb_block) 
            alien.rect.x = 100 + i * 50
            alien.rect.y = 10 + j * 30
            alien_list.add(alien)
            all_sprites_list.add(alien)

    barrier_positions = [100, 250, 400]
    for barrier_x in barrier_positions:
        for j in range(3):
            for i in range(10):
                barrier = Barrier()
                barrier.rect.x = barrier_x + i * 10
                barrier.rect.y = 600 + j * 10
                barrier_list.add(barrier)
                all_sprites_list.add(barrier)

    player = Player('Player.png', scale_size=(40, 40))
    all_sprites_list.add(player)

reset_game()

clock = pygame.time.Clock()
move_direction = 1

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = Bullet()
                bullet.rect.x = player.rect.x + 8
                bullet.rect.y = player.rect.y
                all_sprites_list.add(bullet)
                bullet_list.add(bullet)

    all_sprites_list.update()

    for alien in alien_list:
        alien.rect.x += move_direction

    if any(alien.rect.x > 580 for alien in alien_list):
        move_direction = -1
        for alien in alien_list:
            alien.rect.y += 10
    elif any(alien.rect.x < 0 for alien in alien_list):
        move_direction = 1
        for alien in alien_list:
            alien.rect.y += 10

    for index, alien in enumerate(alien_list):
        if index < 10 and random.random() < 0.001:
            bomb = Bomb('Bomb.png')
            bomb.rect.x = alien.rect.x + 6
            bomb.rect.y = alien.rect.y + 15
            all_sprites_list.add(bomb)
            bomb_list.add(bomb)

        if index >= 10 and random.random() < 0.0005:
            block_bullet = BlockBullet(alien.rect.x + 8, alien.rect.y + 15)
            all_sprites_list.add(block_bullet)
            block_bullet_list.add(block_bullet)

    for bullet in bullet_list:
        alien_hit_list = pygame.sprite.spritecollide(bullet, alien_list, True)
        for alien in alien_hit_list:
            bullet_list.remove(bullet)
            all_sprites_list.remove(bullet)
            score += 20 if alien.is_bomb_block else 10
            print("Score:", score)
            if score % 10 == 0:
                block_speed += 1

        if pygame.sprite.spritecollide(bullet, barrier_list, True):
            bullet_list.remove(bullet)
            all_sprites_list.remove(bullet)

        if bullet.rect.y < -10:
            bullet_list.remove(bullet)
            all_sprites_list.remove(bullet)

    for bomb in bomb_list:
        barrier_hit_list = pygame.sprite.spritecollide(bomb, barrier_list, True)
        if barrier_hit_list:
            bomb_list.remove(bomb)
            all_sprites_list.remove(bomb)
            continue

        if bomb.rect.colliderect(player.rect):
            lives -= 1
            bomb_list.remove(bomb)
            all_sprites_list.remove(bomb)
            print("Lives left:", lives)
            player.reset_position()
            if lives <= 0:
                done = True
                print("You Lost! Final Score:", score)

        if bomb.rect.y > 700:
            bomb_list.remove(bomb)
            all_sprites_list.remove(bomb)

    for block_bullet in block_bullet_list:
        if pygame.sprite.spritecollide(block_bullet, barrier_list, True):
            block_bullet_list.remove(block_bullet)
            all_sprites_list.remove(block_bullet)
            continue

        if block_bullet.rect.colliderect(player.rect):
            lives -= 1
            block_bullet_list.remove(block_bullet)
            all_sprites_list.remove(block_bullet)
            print("Lives left:", lives)
            player.reset_position()
            if lives <= 0:
                done = True
                print("You Lost! Final Score:", score)

        if block_bullet.rect.y > 700:
            block_bullet_list.remove(block_bullet)
            all_sprites_list.remove(block_bullet)

    if len(alien_list) == 0:
        done = True
        print("You Won! Final Score:", score)

    screen.fill(BLACK)
    font = pygame.font.SysFont('Calibri', 25, True, False)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, [0, 600])
    screen.blit(lives_text, [0, 640])

    all_sprites_list.draw(screen)
    pygame.display.flip()
    
    clock.tick(60)

screen.fill(BLACK)
font = pygame.font.SysFont('Calibri', 50, True, False)
result_text = "You Won!" if lives > 0 else "You Died!"
game_over_text = font.render(result_text, True, WHITE)
final_score_text = font.render(f"Final Score: {score}", True, WHITE)
screen.blit(game_over_text, [200, 300])
screen.blit(final_score_text, [200, 350])
pygame.display.flip()

pygame.time.delay(3000)
pygame.quit()
