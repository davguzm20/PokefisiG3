import pygame
from config.colors import Colors
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts

class Placeholder:
    def __init__(self, position_x: int, position_y: int, width: int, height: int,
                 asset: str | None = None, text_color: Colors = Colors.WHITE,
                 text_size: int = 20, label: str | None = None,
                 background_color: Colors | None = None):
        self.asset = Assets.load_image(asset, width, height) if asset else None
        self.label = label
        self.text_size = text_size
        self.text_color = text_color.value
        self.background_color = background_color.value if background_color else None
        self.rect = pygame.Rect(position_x, position_y, width, height)

    def draw(self, screen):
        if self.background_color:
            pygame.draw.rect(screen, self.background_color, self.rect)

        if self.asset:
            screen.blit(self.asset, self.rect)
        elif self.label:
            font = Fonts.get_pixelify_sans(self.text_size)
            text_surface = font.render(self.label, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
