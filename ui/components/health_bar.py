import pygame
from config.colors import Colors
from ui.utils.fonts import Fonts

class HealthBar:
    PANEL_W = 70
    PANEL_H = 130
    BAR_W = 16
    BAR_H = 84
    BAR_X = (PANEL_W - BAR_W) // 2
    BAR_Y = 31

    def __init__(self, position_x: int, position_y: int, pokemon=None):
        self.position_x = position_x
        self.position_y = position_y
        self.pokemon = pokemon

    def _get_bar_color(self, ratio: float):
        if ratio > 0.5:
            return (50, 200, 50)
        if ratio > 0.2:
            return (220, 200, 30)
        return (220, 50, 50)

    def draw(self, screen):
        if not self.pokemon:
            return

        px, py = self.position_x, self.position_y
        current_hp = max(0, getattr(self, 'display_hp', self.pokemon.hp))
        max_hp = getattr(self, 'display_max_hp', self.pokemon.current_hp)
        ratio = current_hp / max_hp if max_hp > 0 else 0

        pygame.draw.rect(screen, Colors.DARK_GRAY.value, (px, py, self.PANEL_W, self.PANEL_H), border_radius=4)
        pygame.draw.rect(screen, Colors.LIGHT_GRAY.value, (px, py, self.PANEL_W, self.PANEL_H), 1, border_radius=4)

        font = Fonts.get_font(11)
        name = self.pokemon.name.capitalize()
        name_surf = font.render(name, False, Colors.WHITE.value)
        screen.blit(name_surf, (px + (self.PANEL_W - name_surf.get_width()) // 2, py + 3))

        hp_label = font.render("HP", False, Colors.LIGHT_GRAY.value)
        screen.blit(hp_label, (px + (self.PANEL_W - hp_label.get_width()) // 2, py + 18))

        bx = px + self.BAR_X
        by = py + self.BAR_Y

        pygame.draw.rect(screen, (80, 20, 20), (bx, by, self.BAR_W, self.BAR_H), border_radius=2)
        if ratio > 0:
            fill_h = int(self.BAR_H * ratio)
            bar_color = self._get_bar_color(ratio)
            fill_y = by + self.BAR_H - fill_h
            pygame.draw.rect(screen, bar_color, (bx, fill_y, self.BAR_W, fill_h), border_radius=2)

        hp_text = f"{current_hp}/{max_hp}"
        hp_surf = font.render(hp_text, False, Colors.WHITE.value)
        screen.blit(hp_surf, (px + (self.PANEL_W - hp_surf.get_width()) // 2, py + self.PANEL_H - hp_surf.get_height() - 4))
