import pygame
import copy
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.components.pokemon_card import PokemonCard
from ui.components.button import Button
from ui.components.placeholder import Placeholder
from ui.components.pokemon_stats import PokemonStats
from ui.components.controls_hint import ControlsHint
from pokemon.pokemon_factory import PokemonFactory
from pokemon.motor.bus_de_eventos import bus_de_eventos_global
from config.colors import Colors
from config.controls import Controls

class TeamScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 0
        self.selected_slot = 0
        self.scroll_offset = 0
        self.grid_row = 0
        self.grid_col = 0
        self.on_grid = False

        self.team_pokemons = [None, None, None, None]
        self.team_cards = [
            PokemonCard(position_x=25, position_y=10),
            PokemonCard(position_x=125, position_y=10),
            PokemonCard(position_x=225, position_y=10),
            PokemonCard(position_x=325, position_y=10),
        ]
        self.continue_button = Button(
            position_x=490, position_y=23,
            width=110, height=36,
            label="CONTINUAR",
            text_size=16,
            background_color=Colors.BLUE,
        )
        self.selection_cards = self.build_grid()
        self.pokemon_stats = PokemonStats(position_x=410, position_y=100)
        self.placeholders = [
            Placeholder(
                position_x=0, position_y=0,
                width=640, height=360,
                asset="assets/backgrounds/menus/fondo-campo.png",
            ),
        ]
        self.controls_hint_slot = ControlsHint(show_back=True, select_label="SELECCIONAR", show_click=True)
        self.controls_hint_grid = ControlsHint(show_left=True, show_right=True,
                                                show_up=True, show_down=True,
                                                show_select=True, show_back=True,
                                                select_label="SELECCIONAR",
                                                show_click=True)

    def build_grid(self):
        cards = []

        for row in range(3):
            for col in range(4):
                idx = self.scroll_offset + row * 4 + col
                pokemon = PokemonFactory.pokemons[idx] if idx < len(PokemonFactory.pokemons) else None
                cards.append(PokemonCard(
                    position_x=[25, 125, 225, 325][col],
                    position_y=[100, 178, 256][row],
                    pokemon=pokemon,
                ))

        return cards

    def _update_stats(self):
        idx = self.scroll_offset + self.grid_row * 4 + self.grid_col
        if idx < len(PokemonFactory.pokemons):
            self.pokemon_stats.pokemon = PokemonFactory.pokemons[idx]
        else:
            self.pokemon_stats.pokemon = None
        self.pokemon_stats.rebuild()

    def confirm_team(self):
        bus_de_eventos_global.disparar("ESTABLECER_NUM_POKEMONES", 4)
        bus_de_eventos_global.disparar("ESTABLECER_JUGADOR_COMO_HUMANO", 1, self.team_pokemons)
        bus_de_eventos_global.disparar("ESTABLECER_JUGADOR_COMO_IA", 2, self.scene_manager.difficulty_config[2], PokemonFactory.pokemons)
        self.scene_manager.juego.configurar_equipo_aleatoriamente(2, PokemonFactory.pokemons)
        bus_de_eventos_global.disparar("INICIALIZAR_COMBATE")
        self.scene_manager.change_scene(SceneType.COMBAT)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.on_grid:
                for idx, card in enumerate(self.selection_cards):
                    if card.rect.collidepoint(event.pos):
                        r, c = idx // 4, idx % 4
                        self.grid_row = r
                        self.grid_col = c
                        grid_idx = self.scroll_offset + r * 4 + c
                        if grid_idx < len(PokemonFactory.pokemons):
                            pokemon = copy.deepcopy(PokemonFactory.pokemons[grid_idx])
                            self.team_pokemons[self.selected_slot] = pokemon
                            self.team_cards[self.selected_slot] = PokemonCard(
                                position_x=self.team_cards[self.selected_slot].rect.x,
                                position_y=self.team_cards[self.selected_slot].rect.y,
                                pokemon=pokemon,
                            )
                        self.on_grid = False
                        return
            else:
                for idx, card in enumerate(self.team_cards):
                    if card.rect.collidepoint(event.pos):
                        self.selected_index = idx
                        self.selected_slot = idx
                        self.on_grid = True
                        self._update_stats()
                        return

                if all(self.team_pokemons) and self.continue_button.is_selected(event.pos):
                    self.selected_index = 4
                    self.confirm_team()
                    return

        if event.type == pygame.KEYDOWN:

            if not self.on_grid:
                max_items = 5 if all(self.team_pokemons) else 4

                if event.key == Controls.LEFT.value:
                    self.selected_index = (self.selected_index - 1) % max_items

                elif event.key == Controls.RIGHT.value:
                    self.selected_index = (self.selected_index + 1) % max_items

                elif event.key in Controls.SELECT.value:
                    if self.selected_index < 4:
                        self.selected_slot = self.selected_index
                        self.on_grid = True
                        self._update_stats()
                    else:
                        self.confirm_team()

                elif event.key in Controls.BACK.value:
                    self.scene_manager.change_scene(SceneType.DIFFICULTY)

            elif self.on_grid:
                if event.key == Controls.LEFT.value:
                    self.grid_col = (self.grid_col - 1) % 4
                    self._update_stats()

                elif event.key == Controls.RIGHT.value:
                    self.grid_col = (self.grid_col + 1) % 4
                    self._update_stats()

                elif event.key == Controls.UP.value:
                    if self.grid_row > 0:
                        self.grid_row -= 1
                    elif self.scroll_offset > 0:
                        self.scroll_offset -= 4
                        self.selection_cards = self.build_grid()
                    self._update_stats()

                elif event.key == Controls.DOWN.value:
                    if self.grid_row < 2:
                        self.grid_row += 1
                    else:
                        max_offset = max(0, len(PokemonFactory.pokemons) - 12)
                        if self.scroll_offset < max_offset:
                            self.scroll_offset += 4
                            self.selection_cards = self.build_grid()
                    self._update_stats()

                elif event.key in Controls.SELECT.value:
                    idx = self.scroll_offset + self.grid_row * 4 + self.grid_col

                    if idx < len(PokemonFactory.pokemons):
                        pokemon = copy.deepcopy(PokemonFactory.pokemons[idx])
                        self.team_pokemons[self.selected_slot] = pokemon
                        self.team_cards[self.selected_slot] = PokemonCard(
                            position_x=self.team_cards[self.selected_slot].rect.x,
                            position_y=self.team_cards[self.selected_slot].rect.y,
                            pokemon=pokemon,
                        )

                    self.on_grid = False

                elif event.key in Controls.BACK.value:
                    self.on_grid = False

    def draw(self, screen):
        for p in self.placeholders:
            p.draw(screen)

        for idx, card in enumerate(self.team_cards):
            card.draw(screen, is_selected=(idx == self.selected_index and not self.on_grid))

        if all(self.team_pokemons) and not self.on_grid:
            self.continue_button.draw(screen, self.selected_index == 4)

        for idx, card in enumerate(self.selection_cards):
            r, c = idx // 4, idx % 4
            card.draw(screen, is_selected=(r == self.grid_row and c == self.grid_col and self.on_grid))

        self.pokemon_stats.draw(screen)

        if self.on_grid:
            self.controls_hint_grid.draw(screen)
        else:
            self.controls_hint_slot.draw(screen)
