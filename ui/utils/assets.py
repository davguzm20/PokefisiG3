import os
import pygame

class Assets:
    @staticmethod
    def load_image(path: str, width: int | None = None, height: int | None = None) -> pygame.Surface | None:
        base, _ = os.path.splitext(path)

        for full in (path, base + ".png"):
            if not os.path.exists(full):
                continue

            try:
                raw = pygame.image.load(os.path.normpath(full))
            except pygame.error:
                continue

            try:
                raw = raw.convert_alpha()
            except pygame.error:
                try:
                    raw = raw.convert()
                except pygame.error:
                    continue

            if width and height:
                return pygame.transform.scale(raw, (width, height))
            return raw
        return None

    @staticmethod
    def load_gif(path: str, width: int | None = None, height: int | None = None) -> pygame.Surface | None:
        base, _ = os.path.splitext(path)

        for full in (path, base + ".gif"):
            if not os.path.exists(full):
                continue

            try:
                raw = pygame.image.load(os.path.normpath(full))
            except pygame.error:
                continue

            try:
                raw = raw.convert()
            except pygame.error:
                continue

            if width and height:
                return pygame.transform.scale(raw, (width, height))
            return raw
        return None
