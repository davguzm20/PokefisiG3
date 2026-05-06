import pygame
from config.colors import Colors
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts

class Placeholder:
    def __init__(self, position_x: int, position_y: int, width: int, height: int,
            asset: str, color: Colors = Colors.WHITE,
            text_size: int = 20, label: str | None = None):
        self.asset = Assets.load_image(asset, width, height)
        self.label = label if label is not None else asset
        self.text_size = text_size
        self.color = color.value
        self.rect = pygame.Rect(position_x, position_y, width, height)

    def draw(self, screen):
        if self.asset:
            screen.blit(self.asset, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect, 3)

            font = Fonts.get_pixelify_sans(self.text_size)
            text_surface = font.render(self.label, True, self.color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
