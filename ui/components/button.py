import pygame
from config.colors import Colors
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts

class Button:
    def __init__(self, position_x: int, position_y: int, width: int, height: int,
            asset: str, text_size: int = 20,
            normal_color: Colors = Colors.WHITE,
            selected_color: Colors = Colors.GOLD,
            label: str | None = None):
        self.asset = Assets.load_image(asset, width, height)
        self.label = label
        self.text_size = text_size
        self.normal_color = normal_color.value
        self.selected_color = selected_color.value
        self.rect = pygame.Rect(position_x, position_y, width, height)

    def draw(self, screen, is_selected):
        if self.asset:
            screen.blit(self.asset, self.rect)

            if is_selected:
                pygame.draw.rect(screen, self.selected_color, self.rect, 3)
        else:
            color = self.selected_color if is_selected else self.normal_color
            pygame.draw.rect(screen, color, self.rect, 3)

            font = Fonts.get_pixelify_sans(self.text_size)
            text_surface = font.render(self.label, True, color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_selected(self, mouse_position: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_position)
