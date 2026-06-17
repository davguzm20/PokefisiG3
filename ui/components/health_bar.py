import pygame
from config.colors import Colors
from ui.utils.fonts import Fonts
from ui.utils.assets import Assets

class HealthBar:
    PANEL_W = 105
    PANEL_H = 135
    BAR_W = 16
    BAR_H = 52
    BAR_X = (PANEL_W - BAR_W) // 2
    BAR_Y = 45
    POKEBALL_SIZE = 16
    POKEBALL_GAP = 4
    POKEBALL_Y = 119
    _pokeball_cache = None
    _pokeball_gray_cache = None

    def __init__(self, position_x: int, position_y: int, pokemon=None):
        self.position_x = position_x
        self.position_y = position_y
        self.pokemon = pokemon
        self.team_total = 0
        self.team_alive = 0

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
        max_hp = getattr(self, 'display_max_hp', self.pokemon.max_hp)

        if getattr(self, '_hp_animating', False):
            target = self._hp_target
            diff = target - current_hp
            if abs(diff) < 0.5:
                current_hp = target
                self._hp_animating = False
                if hasattr(self, '_hp_target'):
                    del self._hp_target
                if hasattr(self, 'display_hp'):
                    del self.display_hp
                if hasattr(self, 'display_max_hp'):
                    del self.display_max_hp
                max_hp = getattr(self, 'display_max_hp', self.pokemon.max_hp)
            else:
                current_hp += diff * 0.2
                self.display_hp = current_hp

        ratio = current_hp / max_hp if max_hp > 0 else 0

        pygame.draw.rect(screen, Colors.DARK_GRAY.value, (px, py, self.PANEL_W, self.PANEL_H), border_radius=4)
        pygame.draw.rect(screen, Colors.LIGHT_GRAY.value, (px, py, self.PANEL_W, self.PANEL_H), 1, border_radius=4)

        font = Fonts.get_font(18)
        name = self.pokemon.name.capitalize()
        name_surf = font.render(name, False, Colors.WHITE.value)
        name_shadow = font.render(name, False, Colors.BLACK.value)
        name_x = px + (self.PANEL_W - name_surf.get_width()) // 2
        screen.blit(name_shadow, (name_x + 1, py + 3 + 1))
        screen.blit(name_surf, (name_x, py + 3))

        hp_label = font.render("HP", False, Colors.LIGHT_GRAY.value)
        hp_shadow = font.render("HP", False, Colors.BLACK.value)
        hp_label_x = px + (self.PANEL_W - hp_label.get_width()) // 2
        screen.blit(hp_shadow, (hp_label_x + 1, py + 25 + 1))
        screen.blit(hp_label, (hp_label_x, py + 25))

        bx = px + self.BAR_X
        by = py + self.BAR_Y

        pygame.draw.rect(screen, (80, 20, 20), (bx, by, self.BAR_W, self.BAR_H), border_radius=2)
        if ratio > 0:
            fill_h = int(self.BAR_H * ratio)
            bar_color = self._get_bar_color(ratio)
            fill_y = by + self.BAR_H - fill_h
            pygame.draw.rect(screen, bar_color, (bx, fill_y, self.BAR_W, fill_h), border_radius=2)

        hp_text = f"{round(current_hp, 2)}/{round(max_hp, 2)}"
        hp_surf = font.render(hp_text, False, Colors.WHITE.value)
        hp_shadow = font.render(hp_text, False, Colors.BLACK.value)
        hp_x = px + (self.PANEL_W - hp_surf.get_width()) // 2
        screen.blit(hp_shadow, (hp_x + 1, py + self.PANEL_H - hp_surf.get_height() - 15 + 1))
        screen.blit(hp_surf, (hp_x, py + self.PANEL_H - hp_surf.get_height() - 15))

        if self.team_total > 0:
            if not HealthBar._pokeball_cache:
                HealthBar._pokeball_cache = Assets.load_image("assets/ui/frames/pokeball.png", self.POKEBALL_SIZE, self.POKEBALL_SIZE)
                if HealthBar._pokeball_cache:
                    gray = pygame.transform.grayscale(HealthBar._pokeball_cache)
                    gray.set_alpha(128)
                    HealthBar._pokeball_gray_cache = gray
            if HealthBar._pokeball_cache:
                total_w = self.team_total * self.POKEBALL_SIZE + (self.team_total - 1) * self.POKEBALL_GAP
                start_x = px + (self.PANEL_W - total_w) // 2
                for i in range(self.team_total):
                    x = start_x + i * (self.POKEBALL_SIZE + self.POKEBALL_GAP)
                    y = py + self.POKEBALL_Y
                    if i < self.team_alive:
                        screen.blit(HealthBar._pokeball_cache, (x, y))
                    elif HealthBar._pokeball_gray_cache:
                        screen.blit(HealthBar._pokeball_gray_cache, (x, y))
