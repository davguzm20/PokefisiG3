import pygame
from config.colors import Colors
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts

class Placeholder:
    def __init__(self, position_x: int, position_y: int, width: int, height: int,
                 asset: str | None = None, text_color: Colors = Colors.WHITE,
                 text_size: int = 20, label: str | None = None,
                 background_color: Colors | None = None):
        self.position_x = position_x
        self.position_y = position_y
        self.width = width
        self.height = height
        self.asset_path = asset
        self.label = label
        self.text_size = text_size
        self.text_color = text_color
        self.background_color = background_color

    def draw(self, screen):
        rect = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
        background = self.background_color.value if self.background_color else None
        text_color = self.text_color.value

        if background:
            pygame.draw.rect(screen, background, rect)

        if self.asset_path:
            loaded_asset = Assets.load_image(self.asset_path, self.width, self.height)

            if loaded_asset:
                screen.blit(loaded_asset, rect)
        
        if self.label:
            font = Fonts.get_font(self.text_size)
            text_surface = font.render(self.label, False, text_color)
            shadow = font.render(self.label, False, Colors.BLACK.value)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
            screen.blit(text_surface, text_rect)
