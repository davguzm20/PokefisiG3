import os
import pygame

class Assets:
    @staticmethod
    def load_image(path: str, width: int | None = None, height: int | None = None):
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
    def load_gif(path: str, width: int | None = None, height: int | None = None):
        base, _ = os.path.splitext(path)

        for full in (path, base + ".gif"):
            if not os.path.exists(full):
                continue

            try:
                from PIL import Image
                pil = Image.open(full)
                frames = []

                for index in range(pil.n_frames):
                    pil.seek(index)
                    frame = pil.convert("RGBA")
                    raw = pygame.image.frombytes(frame.tobytes(), frame.size, "RGBA")
                    raw = raw.convert_alpha()

                    if width and height:
                        raw = pygame.transform.scale(raw, (width, height))

                    duration = pil.info.get("duration", 100)
                    frames.append((raw, duration))

                return frames
            except ImportError:
                try:
                    raw = pygame.image.load(os.path.normpath(full))

                    try:
                        raw = raw.convert_alpha()
                    except pygame.error:
                        try:
                            raw = raw.convert()
                        except pygame.error:
                            return None

                    if width and height:
                        raw = pygame.transform.scale(raw, (width, height))

                    return [(raw, 100)]
                except pygame.error:
                    return None

        return None
