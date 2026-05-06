import pygame
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts
from pokemon.models.pokemon import Pokemon
from config.colors import Colors

class PokemonCard:
    WIDTH = 65
    HEIGHT = 60

    def __init__(self, position_x: int, position_y: int, pokemon: Pokemon | None = None,
                 selected_color: Colors = Colors.GOLD):
        self.selected_color = selected_color.value
        self.rect = pygame.Rect(position_x, position_y, self.WIDTH, self.HEIGHT)
        self.frame = Assets.load_image("assets/ui/frames/cuadro-seleccion-pokemon.png",
                                       self.WIDTH, self.HEIGHT)
        self.sprite = None
        self.types = []
        self.name = ""
        self.type_icons = []

        if pokemon:
            self.sprite = Assets.load_image(pokemon.sprites.mini_regular, 27, 25)
            self.types = pokemon.types
            self.name = pokemon.name
            self.type_icons = [
                Assets.load_image(f"assets/ui/type-icons/{t.value}.png", 11, 7)
                for t in self.types
            ]

    def draw(self, screen: pygame.Surface, is_selected = False):
        cx = self.rect.centerx

        screen.blit(self.frame, self.rect)

        if self.sprite:
            screen.blit(self.sprite, (cx - 13, self.rect.y + 9))

        font = Fonts.get_pixelify_sans(8)
        name_surface = font.render(self.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(centerx=cx, y=self.rect.y + 36)
        shadow_surface = font.render(self.name, True, (0, 0, 0))
        screen.blit(shadow_surface, (name_rect.x + 1, name_rect.y + 1))
        screen.blit(name_surface, name_rect)

        if self.type_icons:
            total_width = len(self.type_icons) * 11 + (len(self.type_icons) - 1) * 4
            start_x = cx - total_width // 2

            for i, icon in enumerate(self.type_icons):
                
                if icon:
                    x = start_x + i * 15
                    screen.blit(icon, (x, self.rect.y + 47))

        if is_selected:
            pygame.draw.rect(screen, self.selected_color, self.rect, 3)
