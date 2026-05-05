import pygame

class Placeholder:
    def __init__(self, x, y, ancho, alto, nombre_asset, color=(100,100,100), borde=2, image_path=None):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.nombre_asset = nombre_asset
        self.color = color
        self.borde = borde
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.image = None
        if image_path:
            try:
                raw = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(raw, (ancho, alto))
            except Exception:
                self.image = None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect, self.borde)
            font = pygame.font.Font(None, 18)
            text_surface = font.render(self.nombre_asset, True, self.color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
