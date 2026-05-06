import os
import pygame

class Assets:
    @staticmethod
    def load_image(path: str, width: int | None = None, height: int | None = None) -> pygame.Surface | None:
        base, _ = os.path.splitext(path)
        for ext in ("", ".png", ".gif"):
            full = base + ext if ext else path
            if os.path.exists(full):
                try:
                    raw = pygame.image.load(full).convert_alpha()
                    if width and height:
                        return pygame.transform.scale(raw, (width, height))
                    return raw
                except pygame.error:
                    return None
        return None