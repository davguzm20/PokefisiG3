import pygame
from config.colors import Colors
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts

class Button:
    def __init__(self, position_x: int, position_y: int, width: int, height: int,
                 asset: str | None = None, text_size: int = 20,
                 text_color: Colors = Colors.WHITE,
                 normal_color: Colors = Colors.WHITE,
                 selected_color: Colors = Colors.GOLD,
                 label: str | None = None,
                 background_color: Colors | None = None,
                 border_size: int = 3,
                 border_color: Colors = Colors.GOLD):
        self.asset = Assets.load_image(asset, width, height) if asset else None
        self.label = label
        self.text_size = text_size
        self.text_color = text_color.value
        self.normal_color = normal_color.value
        self.selected_color = selected_color.value
        self.background_color = background_color.value if background_color else None
        self.border_size = border_size
        self.border_color = border_color.value
        self.rect = pygame.Rect(position_x, position_y, width, height)

    def draw(self, screen, is_selected):
        if self.background_color:
            pygame.draw.rect(screen, self.background_color, self.rect)

        if self.asset:
            screen.blit(self.asset, self.rect)
        else:
            font = Fonts.get_pixelify_sans(self.text_size)
            text_surface = font.render(self.label, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

        if is_selected:
            pygame.draw.rect(screen, self.border_color, self.rect, self.border_size)

    def is_selected(self, mouse_position: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_position)
