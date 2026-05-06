import os
import pygame

class Assets:
    @staticmethod
    def load_image(path: str, width: int, height: int) -> pygame.Surface | None:
        base, _ = os.path.splitext(path)
        for ext in ("", ".png", ".gif"):
            full = base + ext if ext else path
            if os.path.exists(full):
                try:
                    raw = pygame.image.load(full).convert_alpha()
                    return pygame.transform.scale(raw, (width, height))
                except pygame.error:
                    return None
        return None