import pygame

class Button:
    def __init__(self, position_x, position_y, width, height, nombre_asset, text_size, normal_color, selected_color, image_path=None):
        self.position_x = position_x
        self.position_y = position_y
        self.width = width
        self.height = height
        self.nombre_asset = nombre_asset
        self.text_size = text_size
        self.normal_color = normal_color
        self.selected_color = selected_color
        self.rect = pygame.Rect(position_x, position_y, width, height)
        self.image = None
        if image_path:
            try:
                raw = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(raw, (width, height))
            except Exception:
                self.image = None

    def draw(self, screen, is_selected):
        if self.image:
            screen.blit(self.image, self.rect)
            if is_selected:
                pygame.draw.rect(screen, self.selected_color, self.rect, 2)
        else:
            color = self.selected_color if is_selected else self.normal_color
            pygame.draw.rect(screen, color, self.rect, 2)
            font = pygame.font.Font(None, self.text_size)
            text_surface = font.render(self.nombre_asset, True, color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_selected(self, mouse_position):
        return self.rect.collidepoint(mouse_position)
