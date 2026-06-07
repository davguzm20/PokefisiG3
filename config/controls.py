import pygame
from enum import Enum

class Controls(Enum):
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    SELECT = (pygame.K_RETURN, pygame.K_z, 1)
    BACK = (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_x)