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
        self.position_x = position_x
        self.position_y = position_y
        self.width = width
        self.height = height
        self.asset_path = asset
        self.label = label
        self.text_size = text_size
        self.text_color = text_color
        self.normal_color = normal_color
        self.selected_color = selected_color
        self.background_color = background_color
        self.border_size = border_size
        self.border_color = border_color

    def draw(self, screen, is_selected):
        rect = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
        background = self.background_color.value if self.background_color else None
        selected_border_color = self.selected_color.value if is_selected else None
        text_color = self.text_color.value

        if background:
            pygame.draw.rect(screen, background, rect)

        if self.asset_path:
            loaded_asset = Assets.load_image(self.asset_path, self.width, self.height)

            if loaded_asset:
                screen.blit(loaded_asset, rect)
                
        elif self.label:
            font = Fonts.get_font(self.text_size)
            text_surface = font.render(self.label, False, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

        if is_selected:
            pygame.draw.rect(screen, selected_border_color, rect, self.border_size)

    def is_selected(self, mouse_position: tuple[int, int]) -> bool:
        return pygame.Rect(
            self.position_x, self.position_y, self.width, self.height
        ).collidepoint(mouse_position)
