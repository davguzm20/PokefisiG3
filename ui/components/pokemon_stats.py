import pygame
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts
from config.colors import Colors

class PokemonStats:
    WIDTH = 205
    HEIGHT = 233

    def __init__(self, position_x: int, position_y: int):
        self.position_x = position_x
        self.position_y = position_y
        self.pokemon = None
        self.frames = []
        self.frame_index = 0
        self.last_frame_time = 0

    def rebuild(self):
        self.frames = []
        self.frame_index = 0

    def draw(self, screen):
        px, py = self.position_x, self.position_y

        frame = Assets.load_image("assets/ui/frames/cuadro-seleccion-pokemon.png", self.WIDTH, self.HEIGHT)
        if frame:
            screen.blit(frame, (px, py))

        if not self.pokemon:
            return

        if not self.frames:
            frames_data = Assets.load_gif(self.pokemon.sprites.regular)
            if frames_data:
                for surface, duration in frames_data:
                    self.frames.append((surface, duration))
                self.last_frame_time = pygame.time.get_ticks()

        if self.frames:
            now = pygame.time.get_ticks()
            frame = self.frames[self.frame_index]
            if now - self.last_frame_time >= frame[1]:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.last_frame_time = now
                frame = self.frames[self.frame_index]
            sprite_x = px + (self.WIDTH - frame[0].get_width()) // 2
            screen.blit(frame[0], (sprite_x, py + 24))

        font = Fonts.get_font(18)
        small = Fonts.get_font(16)

        name = self.pokemon.name.capitalize()
        name_surf = font.render(name, False, Colors.WHITE.value)
        name_shadow = font.render(name, False, Colors.BLACK.value)
        name_x = px + (self.WIDTH - name_surf.get_width()) // 2
        screen.blit(name_shadow, (name_x + 1, py + 90 + 1))
        screen.blit(name_surf, (name_x, py + 90))

        type_icons = [
            Assets.load_image(f"assets/ui/type-mini/{t.value}.png", 32, 14)
            for t in self.pokemon.types
        ]
        if type_icons:
            total_w = len(type_icons) * 32 + (len(type_icons) - 1) * 4
            start_x = px + (self.WIDTH - total_w) // 2
            for i, icon in enumerate(type_icons):
                if icon:
                    screen.blit(icon, (start_x + i * 36, py + 114))

        stats = [
            ("HP", self.pokemon.max_hp),
            ("ATK", self.pokemon.attack),
            ("DEF", self.pokemon.defense),
            ("SPA", self.pokemon.special_attack),
            ("SPD", self.pokemon.special_defense),
            ("SPE", self.pokemon.speed),
        ]

        row_y = [140, 164, 188]
        col_w = self.WIDTH // 2
        gap = 8

        for row_idx in range(3):
            y = py + row_y[row_idx]
            for col_idx in range(2):
                label, value = stats[row_idx * 2 + col_idx]
                cx = px + col_w * col_idx + col_w // 2
                lbl = small.render(label, False, Colors.LIGHT_GRAY.value)
                val = small.render(str(value), False, Colors.WHITE.value)
                val_shadow = small.render(str(value), False, Colors.BLACK.value)
                pair_w = lbl.get_width() + gap + val.get_width()
                start_x = cx - pair_w // 2
                screen.blit(lbl, (start_x, y))
                screen.blit(val_shadow, (start_x + lbl.get_width() + gap + 1, y + 1))
                screen.blit(val, (start_x + lbl.get_width() + gap, y))
