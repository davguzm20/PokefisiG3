import pygame

class Fonts:
    PIXELIFY_SANS = "config/fonts/PixelifySans-VariableFont_wght.ttf"
    MINECRAFT = "config\fonts\Minecraft.ttf"

    @staticmethod
    def get_font(size: int):
        try:
            return pygame.font.Font(Fonts.MINECRAFT, size)
        except (FileNotFoundError, pygame.error):
            return pygame.font.Font(None, size)