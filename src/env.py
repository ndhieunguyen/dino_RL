from pygame.sprite import AbstractGroup
from random import randrange, choice
from utils import *
import pygame
import os

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("AuT-Rex")


class Dino:
    def __init__(self, size_x=-1, size_y=-1) -> None:
        # Prepare running dino
        self.images_run, self.rects_run = load_sprite_sheet(
            path=os.path.join("assets", "dino.png"),
            nx=5,
            ny=1,
            scale_x=size_x,
            scale_y=size_y,
            colorkey=-1,
        )
        self.rects_run.bottom = int(0.98 * HEIGHT)
        self.rects_run.left = WIDTH / 15

        # Prepare ducking dino
        self.images_duck, self.rects_duck = load_sprite_sheet(
            path=os.path.join("assets", "dino_ducking.png"),
            nx=2,
            ny=1,
            scale_x=59,
            scale_y=size_y,
            colorkey=-1,
        )

        # First frame
        self.image = self.images_run[0]
        self.index = 0
        self.counter = 0
        self.score = 0

        self.is_jumping = False
        self.is_ducking = False
        self.is_blinking = False
        self.is_dead = False

        self.movement = [0, 0]
        self.jump_speed = 11.5

        self.running_width = self.rects_run.width
        self.ducking_width = self.rects_duck.width

    def draw(self):
        SCREEN.blit(self.image, self.rects_run)

    def check_bounds(self):
        if self.rect.bottom > int(0.98 * HEIGHT):
            self.rect.bottom = int(0.98 * HEIGHT)
            self.isJumping = False

    def update(self):
        if self.is_jumping:
            self.movement[1] = self.movement + GRAVITY
            self.index = 0
        elif self.is_blinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1) % 2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1) % 2

        elif self.is_ducking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2 + 2

        if self.is_dead:
            self.index = 4

        if self.is_ducking:
            self.image = self.images_duck[(self.index) % 2]
            self.rects_run.width = self.ducking_width
        else:
            self.image = self.images_run[self.index]
            self.rects_run.width = self.running_width

        self.rects_run = self.rects_run.move(self.movement)
        self.check_bounds()

        if not self.is_dead and self.counter % 7 == 6 and not self.is_blinking:
            self.score += 1

        self.counter = self.counter + 1


class Cactus(pygame.sprite.Sprite):
    def __init__(self, speed=5, size_x=-1, size_y=-1):
        super().__init__()
        self.images, self.rect = load_sprite_sheet(
            os.path.join("assets", "cacti-small.png"),
            nx=[2, 3, 6],
            ny=1,
            scale_x=size_x,
            scale_y=size_y,
            colorkey=-1,
        )
        self.rect.bottom = int(0.98 * HEIGHT)
        self.rect.left = WIDTH + self.rect.width
        self.image = self.images[randrange(0, 11)]
        self.movement = [-1 * speed, 0]

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)

        if self.rect.right < 0:
            self.kill()


class Ptera(pygame.sprite.Sprite):
    def __init__(self, speed=5, size_x=-1, size_y=-1) -> None:
        super().__init__()
        self.images, self.rect = load_sprite_sheet(
            os.path.join("assets", "ptera.png"),
            nx=2,
            ny=1,
            scale_x=size_x,
            scale_y=size_y,
            colorkey=-1,
        )
        self.ptera_height = [HEIGHT * 0.82, HEIGHT * 0.75, HEIGHT * 0.60, HEIGHT * 0.48]
        self.rect.centery = self.ptera_height[randrange(0, 4)]
        self.rect.left = WIDTH + self.rect.width
        self.image = self.images[0]
        self.movement = [-1 * speed, 0]
        self.index = 0
        self.counter = 0

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index + 1) % 2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = self.counter + 1
        if self.rect.right < 0:
            self.kill()


class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image, self.rect = load_image(
            os.path.join("assets", "cloud.png"),
            size_x=int(90 * 30 / 42),
            size_y=30,
            colorkey=-1,
        )
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1 * self.speed, 0]

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()


class Ground:
    def __init__(self, speed=-5) -> None:
        self.image, self.rect = load_image(
            os.path.join("assets", "ground.png"),
            size_x=-1,
            size_y=-1,
            colorkey=-1,
        )
        self.image1, self.rect1 = load_image(
            os.path.join("assets", "ground.png"),
            size_x=-1,
            size_y=-1,
            colorkey=-1,
        )
        self.rect.bottom = HEIGHT
        self.rect1.bottom = HEIGHT
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        SCREEN.blit(self.image, self.rect)
        SCREEN.blit(self.image1, self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right


class Scoreboard:
    def __init__(self, x=-1, y=-1):
        self.score = 0
        self.temp_images, self.temp_rect = load_sprite_sheet(
            os.path.join("assets", "numbers.png"),
            nx=12,
            ny=1,
            scale_x=11,
            scale_y=int(11 * 6 / 5),
            colorkey=-1,
        )
        self.image = Surface((55, int(11 * 6 / 5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = WIDTH * 0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = HEIGHT * 0.1
        else:
            self.rect.top = y

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def update(self, score):
        score_digits = create_score(score)
        self.image.fill(BACKGROUND_COLOR)
        if len(score_digits) == 6:
            score_digits = score_digits[1:]
        for s in score_digits:
            self.image.blit(self.temp_images[s], self.temp_rect)
            self.temp_rect.left += self.temp_rect.width
        self.temp_rect.left = 0


class DinoGame(object):
    def __init__(self) -> None:
        self.gamespeed = 5
        self.game_over = False
        self.game_quit = False
        self.agent = Dino(44, 47)
        self.round = Ground(-1 * self.gamespeed)
        self.scb = Scoreboard()
        self.highsc = Scoreboard(width * 0.78)
        self.counter = 0

        self.cacti = Group()
        self.pteras = Group()
        self.clouds = Group()
        self.last_obstacle = Group()

        Cactus.containers = self.cacti
        Ptera.containers = self.pteras
        Cloud.containers = self.clouds

        self.retbutton_image, self.retbutton_rect = load_image("replay_button.png", 35, 31, -1)
        self.gameover_image, self.gameover_rect = load_image("game_over.png", 190, 11, -1)

        self.temp_images, self.temp_rect = load_sprite_sheet("numbers.png", 12, 1, 11, int(11 * 6 / 5), -1)
        self.HI_image = Surface((22, int(11 * 6 / 5)))
        self.HI_rect = self.HI_image.get_rect()
        self.HI_image.fill(background_col)
        self.HI_image.blit(self.temp_images[10], self.temp_rect)
        self.temp_rect.left += self.temp_rect.width
        self.HI_image.blit(self.temp_images[11], self.temp_rect)
        self.HI_rect.top = height * 0.1
        self.HI_rect.left = width * 0.73
