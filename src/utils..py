import cv2
import numpy as np
from pygame import RLEACCEL
from pygame import transform
from pygame import Rect, Surface
from pygame.image import load

WIDTH, HEIGHT = 600, 150


def transform_image(image, size_x=-1, size_y=-1, colorkey=None):
    if colorkey:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if size_x != -1 or size_y != -1:
        image = transform.scale(image, (size_x, size_y))

    return image


def load_image(path, size_x=-1, size_y=-1, colorkey=None):
    image = load(path)
    image = image.convert()
    image = transform_image(image, size_x, size_y, colorkey)

    return image, image.get_rect()


def load_sprite_sheet(path, nx, ny, scale_x=-1, scale_y=-1, colorkey=None):
    sheet = load(path)
    sheet = sheet.convert()
    sheet_rect = sheet.get_rect()

    size_y = sheet_rect.height / ny
    nx = [nx] if isinstance(nx, int) else nx
    size_x_list = [sheet_rect.width / nx_ele for nx_ele in nx]
    sprites = []

    for i in range(0, ny):
        for i_nx, size_x, i_scalex in zip(nx, size_x_list, scale_x):
            for j in range(0, i_nx):
                rect = Rect((j * size_x, i * size_y, size_x, size_y))
                image = Surface(rect.size)
                image = image.convert()
                image.blit(sheet, (0, 0), rect)
                image = transform_image(image, i_scalex, scale_y, colorkey)
                sprites.append(image)
    sprite_rect = sprites[0].get_rect()

    return sprites, sprite_rect


def create_score(number):
    if number < 0:
        return
    number = str(number).rjust(5, "0")
    number = [int(digit) for digit in number]

    return number


def preprocess_image(image, width=84, height=84):
    image = image[:300, :, :]
    image = cv2.resize(image, (width, height))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    return image[None, :, :].astype(np.float32)
