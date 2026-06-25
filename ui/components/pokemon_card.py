import pygame
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts
from pokemon.models.pokemon import Pokemon
from config.colors import Colors

class PokemonCard:
    SIZE = 75

    def __init__(self, position_x: int, position_y: int, pokemon: Pokemon | None = None,
                 selected_color: Colors = Colors.GOLD,
                 show_hp: bool = False,
                 disabled: bool = False):
        self.position_x = position_x
        self.position_y = position_y
        self.pokemon = pokemon
        self.selected_color = selected_color.value
        self.show_hp = show_hp
        self.disabled = disabled

    @property
    def rect(self):
        return pygame.Rect(self.position_x, self.position_y, self.SIZE, self.SIZE)

    def draw(self, screen, is_selected=False):
        rect = pygame.Rect(self.position_x, self.position_y, self.SIZE, self.SIZE)
        frame = Assets.load_image(
            "assets/ui/frames/cuadro-seleccion-pokemon.png",
            self.SIZE, self.SIZE,
        )
        screen.blit(frame, rect)

        center_x = rect.centerx

        if self.pokemon:
            raw_sprite = Assets.load_image(self.pokemon.sprites.mini_regular)

            if raw_sprite:
                sprite = raw_sprite.subsurface((0, 28, 68, 28))
                screen.blit(sprite, (center_x - 34, rect.y + 6))

            name = self.pokemon.name.capitalize()
            font = Fonts.get_font(16)

            name_surface = font.render(name, False, Colors.WHITE.value)
            name_rect = name_surface.get_rect(centerx=center_x, y=rect.y + 35)
            shadow = font.render(name, False, Colors.BLACK.value)
            screen.blit(shadow, (name_rect.x + 1, name_rect.y + 1))
            screen.blit(name_surface, name_rect)

            if self.show_hp:
                hp_text = f"{self.pokemon.hp}/{self.pokemon.max_hp}"
                hp_font = Fonts.get_font(18)
                hp_color = Colors.RED.value if self.disabled else Colors.WHITE.value
                hp_surface = hp_font.render(hp_text, False, hp_color)
                hp_rect = hp_surface.get_rect(centerx=center_x, y=rect.y + 53)
                hp_shadow = hp_font.render(hp_text, False, Colors.BLACK.value)
                screen.blit(hp_shadow, (hp_rect.x + 1, hp_rect.y + 1))
                screen.blit(hp_surface, hp_rect)
            else:
                type_icons = [
                    Assets.load_image(f"assets/ui/type-mini/{t.value}.png", 32, 14)
                    for t in self.pokemon.types
                ]
                if type_icons:
                    total_width = len(type_icons) * 32 + (len(type_icons) - 1) * 3
                    start_x = center_x - total_width // 2

                    for i, icon in enumerate(type_icons):
                        if icon:
                            screen.blit(icon, (start_x + i * 35, rect.y + 53))

        if is_selected and not self.disabled:
            pygame.draw.rect(screen, self.selected_color, rect, 3)

        if self.disabled:
            overlay = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 80))
            screen.blit(overlay, rect)
