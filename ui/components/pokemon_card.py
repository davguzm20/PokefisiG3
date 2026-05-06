import pygame
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts
from pokemon.models.pokemon import Pokemon
from config.colors import Colors

class PokemonCard:
    WIDTH = 70
    HEIGHT = 70

    def __init__(self, position_x: int, position_y: int, pokemon: Pokemon | None = None,
                 selected_color: Colors = Colors.GOLD):
        self.selected_color = selected_color.value
        self.rect = pygame.Rect(position_x, position_y, self.WIDTH, self.HEIGHT)
        self.frame = Assets.load_image(
            "assets/ui/frames/cuadro-seleccion-pokemon.png",
            self.WIDTH, self.HEIGHT,
        )
        self.sprite = None
        self.name = ""
        self.type_icons = []

        if pokemon:
            self.sprite = Assets.load_image(pokemon.sprites.mini_regular)
            if self.sprite:
                self.sprite = self.sprite.subsurface((0, 28, 68, 28))
            self.name = pokemon.name[0].upper() + pokemon.name[1:]
            self.type_icons = [
                Assets.load_image(f"assets/ui/type-mini/{t.value}.png", 16, 7)
                for t in pokemon.types
            ]

    def draw(self, screen, is_selected=False):
        cx = self.rect.centerx

        screen.blit(self.frame, self.rect)

        if self.sprite:
            screen.blit(self.sprite, (cx - 34, self.rect.y + 8))

        font = Fonts.get_pixelify_sans(12)
        name_surface = font.render(self.name, True, Colors.WHITE.value)
        name_rect = name_surface.get_rect(centerx=cx, y=self.rect.y + 37)
        shadow_surface = font.render(self.name, True, Colors.BLACK.value)
        screen.blit(shadow_surface, (name_rect.x + 1, name_rect.y + 1))
        screen.blit(name_surface, name_rect)

        if self.type_icons:
            total_width = len(self.type_icons) * 16 + (len(self.type_icons) - 1) * 3
            start_x = cx - total_width // 2

            for i, icon in enumerate(self.type_icons):
                if icon:
                    screen.blit(icon, (start_x + i * 19, self.rect.y + 55))

        if is_selected:
            pygame.draw.rect(screen, self.selected_color, self.rect, 3)
