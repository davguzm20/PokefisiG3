import pygame

class Fonts:
    PIXELIFY_SANS = "config/fonts/PixelifySans-VariableFont_wght.ttf"

    @staticmethod
    def get_pixelify_sans(size: int):
        try:
            return pygame.font.Font(Fonts.PIXELIFY_SANS, size)
        except (FileNotFoundError, pygame.error):
            return pygame.font.Font(None, size)