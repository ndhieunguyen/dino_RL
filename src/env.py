from pygame.sprite import Group, Sprite
from pygame.sprite import collide_mask
from pygame.surfarray import array3d
from pygame import display, time
import random
from src.utils import *
import torch
import pygame
import os

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

FPS = 60
SCREEN = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("AuT-Rex")


class Dino:
    def __init__(self, size_x=-1, size_y=-1) -> None:
        # Prepare running dino
        self.images_run, self.rect = load_sprite_sheet(
            path=os.path.join("assets", "dino.png"),
            nx=5,
            ny=1,
            scale_x=size_x,
            scale_y=size_y,
            colorkey=-1,
        )
        self.rect.bottom = int(0.98 * HEIGHT)
        self.rect.left = WIDTH / 15

        # Prepare ducking dino
        self.images_duck, self.rect_duck = load_sprite_sheet(
            path=os.path.join("assets", "dino_ducking.png"),
            nx=2,
            ny=1,
            scale_x=59,
            scale_y=size_y,
            colorkey=-1,
        )

        # First frame
        self.image = self.images_run[0]
        self.index = 0  # index of image in image list
        self.counter = 0  # count to determine the frequency of changing the self.index
        self.score = 0  # score of game

        self.is_jumping = False
        self.is_ducking = False
        self.is_blinking = False
        self.is_dead = False

        self.movement = [0, 0]  # [horizontal, vertical]
        self.jump_speed = 11.5

        self.running_width = self.rect.width
        self.ducking_width = self.rect_duck.width

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def check_bounds(self):
        if self.rect.bottom > int(0.98 * HEIGHT):
            self.rect.bottom = int(0.98 * HEIGHT)
            self.is_jumping = False

    def update(self):
        if self.is_jumping:
            self.movement[1] = self.movement[1] + GRAVITY
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
            self.image = self.images_duck[self.index % 2]
            self.rect.width = self.ducking_width
        else:
            self.image = self.images_run[self.index]
            self.rect.width = self.running_width

        self.rect = self.rect.move(self.movement)
        self.check_bounds()

        if not self.is_dead and self.counter % 7 == 6 and not self.is_blinking:
            self.score += 1

        self.counter = self.counter + 1


class Cactus(Sprite):
    def __init__(self, speed=5, size_x=-1, size_y=-1):
        Sprite.__init__(self, self.containers)
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
        self.image = self.images[random.randrange(0, 11)]
        self.movement = [-1 * speed, 0]

    def draw(self):
        SCREEN.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)

        if self.rect.right < 0:
            self.kill()


class Ptera(Sprite):
    def __init__(self, speed=5, size_x=-1, size_y=-1) -> None:
        Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet(
            os.path.join("assets", "ptera.png"),
            nx=2,
            ny=1,
            scale_x=size_x,
            scale_y=size_y,
            colorkey=-1,
        )
        self.ptera_height = [HEIGHT * 0.82, HEIGHT * 0.75, HEIGHT * 0.60, HEIGHT * 0.48]
        self.rect.centery = self.ptera_height[random.randrange(0, 4)]
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
        self.counter += 1
        if self.rect.right < 0:
            self.kill()


class Cloud(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self, self.containers)
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
        self.game_speed = 5
        self.game_over = False
        self.game_quit = False
        self.player_dino = Dino(44, 47)
        self.ground = Ground(-1 * self.game_speed)
        self.scb = Scoreboard()
        self.highsc = Scoreboard(WIDTH * 0.78)
        self.counter = 0

        self.cacti = Group()
        self.pteras = Group()
        self.clouds = Group()
        self.last_obstacle = Group()

        Cactus.containers = self.cacti
        Ptera.containers = self.pteras
        Cloud.containers = self.clouds

        # TODO: add replay button and high score
        # self.retbutton_image, self.retbutton_rect = load_image(
        #     path=os.path.join("assets", "replay_button.png"),
        #     size_x=35,
        #     size_y=31,
        #     colorkey=-1,
        # )
        # self.gameover_image, self.gameover_rect = load_image(
        #     path=os.path.join("assets", "game_over.png"),
        #     size_x=190,
        #     size_y=11,
        #     colorkey=-1,
        # )
        # self.temp_images, self.temp_rect = load_sprite_sheet(
        #     path=os.path.join("assets", "numbers.png"),
        #     nx=12,
        #     ny=1,
        #     scale_x=11,
        #     scale_y=int(11 * 6 / 5),
        #     colorkey=-1,
        # )

        # self.HI_image = Surface((22, int(11 * 6 / 5)))
        # self.HI_rect = self.HI_image.get_rect()
        # self.HI_image.fill(BACKGROUND_COLOR)
        # self.HI_image.blit(self.temp_images[10], self.temp_rect)
        # self.temp_rect.left += self.temp_rect.width
        # self.HI_image.blit(self.temp_images[11], self.temp_rect)
        # self.HI_rect.top = HEIGHT * 0.1
        # self.HI_rect.left = WIDTH * 0.73

    def step(self, action, record=False):
        reward = 0.1
        if action == 0:  # normally run
            reward += 0.01
            self.player_dino.is_ducking = False
        elif action == 1:  # jump
            self.player_dino.is_ducking = False
            if self.player_dino.rect.bottom == int(0.98 * HEIGHT):
                self.player_dino.is_jumping = True
                self.player_dino.movement[1] = -1 * self.player_dino.jump_speed
        elif action == 2:  # duck
            if not (self.player_dino.is_jumping and self.player_dino.is_dead) and self.player_dino.rect.bottom == int(
                0.98 * HEIGHT
            ):
                self.player_dino.is_ducking = True

        # Check collision to the cacti
        for c in self.cacti:
            c.movement[0] = -1 * self.game_speed
            if collide_mask(self.player_dino, c):
                self.player_dino.is_dead = True
                reward = -1
                break
            else:
                if c.rect.right < self.player_dino.rect.left < c.rect.right + self.game_speed + 1:
                    reward = 1
                    break

        # Check collision to the pteras
        for p in self.pteras:
            p.movement[0] = -1 * self.game_speed
            if collide_mask(self.player_dino, p):
                self.player_dino.is_dead = True
                reward = -1
                break
            else:
                if p.rect.right < self.player_dino.rect.left < p.rect.right + self.game_speed + 1:
                    reward = 1
                    break

        if len(self.cacti) < 2:
            if len(self.cacti) == 0 and len(self.pteras) == 0:
                self.last_obstacle.empty()
                self.last_obstacle.add(
                    Cactus(
                        self.game_speed,
                        size_x=[60, 40, 20],
                        size_y=random.choice([40, 45, 50]),
                    )
                )
            else:
                for l in self.last_obstacle:
                    if l.rect.right < WIDTH * 0.7 and random.randrange(0, 50) == 10:
                        self.last_obstacle.empty()
                        self.last_obstacle.add(
                            Cactus(
                                self.game_speed,
                                size_x=[60, 40, 20],
                                size_y=random.choice([40, 45, 50]),
                            )
                        )
        if len(self.pteras) == 0 and len(self.cacti) < 2 and random.randrange(0, 50) == 10 and self.counter > 500:
            for l in self.last_obstacle:
                if l.rect.right < WIDTH * 0.8:
                    self.last_obstacle.empty()
                    self.last_obstacle.add(Ptera(self.game_speed, 46, 40))

        if len(self.clouds) < 5 and random.randrange(0, 300) == 10:
            Cloud(x=WIDTH, y=random.randrange(HEIGHT // 5, HEIGHT // 2))

        self.player_dino.update()
        self.cacti.update()
        self.pteras.update()
        self.clouds.update()
        self.ground.update()
        self.scb.update(self.player_dino.score)

        state = display.get_surface()
        SCREEN.fill(BACKGROUND_COLOR)
        self.ground.draw()
        self.clouds.draw(SCREEN)
        self.scb.draw()
        self.cacti.draw(SCREEN)
        self.pteras.draw(SCREEN)
        self.player_dino.draw()

        display.update()
        clock.tick(FPS)

        if self.player_dino.is_dead:
            self.game_over = True

        self.counter = self.counter + 1

        # if self.game_over:
        #     self.__init__()

        state = array3d(state)
        if record:
            return (
                torch.from_numpy(preprocess_image(state)),
                np.transpose(cv2.cvtColor(state, cv2.COLOR_RGB2BGR), (1, 0, 2)),
                reward,
                not (reward > 0),
            )
        else:
            return (
                torch.from_numpy(preprocess_image(state)),
                reward,
                not (reward > 0),
            )


if __name__ == "__main__":
    game = DinoGame()
    while not game.game_over:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        action = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            action = 1
        elif keys[pygame.K_DOWN]:
            action = 2

        game.step(action=action)
