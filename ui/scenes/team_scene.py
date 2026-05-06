import pygame
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.components.pokemon_card import PokemonCard
from ui.components.placeholder import Placeholder
from pokemon.pokemon_factory import PokemonFactory
from config.controls import Controls

class TeamScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 0
        self.selected_slot = 0
        self.scroll_offset = 0
        self.grid_row = 0
        self.grid_col = 0
        self.mode = "team"

        self.load_pokemons()
        self.team_pokemons = [None, None, None, None]
        self.team_cards = [
            PokemonCard(175, 10, None),
            PokemonCard(250, 10, None),
            PokemonCard(325, 10, None),
            PokemonCard(400, 10, None),
        ]
        self.selection_cards = self.build_grid()
        self.placeholders = [
            Placeholder(0, 0, 640, 360, "assets/backgrounds/menus/fondo-campo.png"),
            Placeholder(0, 78, 640, 20, "SELECCIONA 4 POKEMONES", text_size=8),
        ]

    def load_pokemons(self):
        self.pokemons = PokemonFactory.load_all_pokemons("pokemon/pokemones.json")
        print(f"Fueron cargados {len(self.pokemons)} pokemons")

    def build_grid(self):
        cards = []

        for row in range(3):
            for col in range(4):
                idx = self.scroll_offset + row * 4 + col
                pokemon = self.pokemons[idx] if idx < len(self.pokemons) else None
                cards.append(PokemonCard([175, 250, 325, 400][col], [109, 179, 249][row], pokemon))

        return cards

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if self.mode == "team":
                if event.key == Controls.LEFT.value:
                    self.selected_index = (self.selected_index - 1) % 4

                elif event.key == Controls.RIGHT.value:
                    self.selected_index = (self.selected_index + 1) % 4

                elif event.key in Controls.SELECT.value:
                    self.selected_slot = self.selected_index
                    self.mode = "grid"

                elif event.key in Controls.BACK.value:
                    self.scene_manager.change_scene(SceneType.MENU)

            elif self.mode == "grid":
                if event.key == Controls.LEFT.value:
                    self.grid_col = (self.grid_col - 1) % 4

                elif event.key == Controls.RIGHT.value:
                    self.grid_col = (self.grid_col + 1) % 4

                elif event.key == Controls.UP.value:
                    if self.grid_row > 0:
                        self.grid_row -= 1

                    elif self.scroll_offset > 0:
                        self.scroll_offset -= 4
                        self.selection_cards = self.build_grid()

                elif event.key == Controls.DOWN.value:
                    if self.grid_row < 2:
                        self.grid_row += 1
                    else:
                        max_offset = max(0, len(self.pokemons) - 12)
                        if self.scroll_offset < max_offset:
                            self.scroll_offset += 4
                            self.selection_cards = self.build_grid()

                elif event.key in Controls.SELECT.value:
                    idx = self.scroll_offset + self.grid_row * 4 + self.grid_col

                    if idx < len(self.pokemons):
                        pokemon = self.pokemons[idx]
                        self.team_pokemons[self.selected_slot] = pokemon
                        self.team_cards[self.selected_slot] = PokemonCard(
                            self.team_cards[self.selected_slot].rect.x,
                            self.team_cards[self.selected_slot].rect.y, pokemon)

                    self.mode = "team"

                elif event.key in Controls.BACK.value:
                    self.mode = "team"

    def draw(self, screen):
        for p in self.placeholders:
            p.draw(screen)

        for idx, card in enumerate(self.team_cards):
            card.draw(screen, is_selected=(idx == self.selected_index and self.mode == "team"))

        for idx, card in enumerate(self.selection_cards):
            r, c = idx // 4, idx % 4
            card.draw(screen, is_selected=(r == self.grid_row and c == self.grid_col and self.mode == "grid"))
