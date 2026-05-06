import pygame
from ui.utils.assets import Assets
from pokemon.models.pokemon import Pokemon

class PokemonLayout:
    SIZE = 180
    SCALE = 2

    def __init__(self, position_x: int, position_y: int,
                 pokemon: Pokemon | None = None, number_player: int = 1):
        self.position_x = position_x
        self.position_y = position_y
        self.pokemon = pokemon
        self.number_player = number_player

    def draw(self, screen):
        if self.pokemon:
            if self.number_player == 1:
                sprite_path = self.pokemon.sprites.back
            else:
                sprite_path = self.pokemon.sprites.regular

            sprite_surface = Assets.load_gif(sprite_path)

            if sprite_surface:
                sprite_surface = pygame.transform.flip(sprite_surface, False, False)

                sprite_width = int(sprite_surface.get_width() * self.SCALE)
                sprite_height = int(sprite_surface.get_height() * self.SCALE)

                sprite_surface = pygame.transform.scale(sprite_surface, (sprite_width, sprite_height))

                sprite_position_x = self.position_x + (self.SIZE - sprite_width) // 2
                sprite_position_y = self.position_y + self.SIZE - sprite_height

                screen.blit(sprite_surface, (sprite_position_x, sprite_position_y))
