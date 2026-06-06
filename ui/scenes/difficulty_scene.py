import pygame
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.scenes.enums.difficulty_option import DifficultyOption
from ui.components.button import Button
from ui.components.placeholder import Placeholder
from pokemon.pokemon_factory import PokemonFactory
from pokemon.motor.bus_de_eventos import bus_de_eventos_global
from config.controls import Controls

from pokemon.motor.juego_interfaz import Acciones

class DifficultyScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 0
        self.buttons = {
            DifficultyOption.EASY: Button(
                position_x=40, position_y=282,
                width=120, height=44,
                asset="assets/ui/buttons/button-easy.png",
            ),
            DifficultyOption.INTERMEDIATE: Button(
                position_x=260, position_y=282,
                width=120, height=44,
                asset="assets/ui/buttons/button-intermediate.png",
            ),
            DifficultyOption.HARD: Button(
                position_x=480, position_y=282,
                width=120, height=44,
                asset="assets/ui/buttons/button-hard.png",
            ),
        }
        self.placeholders = [
            Placeholder(
                position_x=0, position_y=0,
                width=640, height=360,
                asset="assets/backgrounds/menus/fondo-campo.png",
            ),
            Placeholder(
                position_x=110, position_y=105,
                width=420, height=135,
                asset="assets/ui/titles/titulo-principal.png",
            ),
        ]
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == Controls.LEFT.value:
                self.selected_index = (self.selected_index - 1) % len(DifficultyOption)
            elif event.key == Controls.RIGHT.value:
                self.selected_index = (self.selected_index + 1) % len(DifficultyOption)
            elif event.key in Controls.SELECT.value:
                self.select_option()
            elif event.key in Controls.BACK.value:
                self.scene_manager.change_scene(SceneType.MODE)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for index, option in enumerate(self.buttons):
                    if self.buttons[option].is_selected(event.pos):
                        self.selected_index = index
                        self.select_option()

    def select_option(self):
        option = list(self.buttons.keys())[self.selected_index]

        level = option.value
        sm = self.scene_manager

        if sm.game_mode == "PVAI":
            sm.difficulty_config[2] = level
            sm.change_scene(SceneType.TEAM)
            bus_de_eventos_global.disparar("ESTABLECER_JUGADOR_COMO_IA", 2, sm.difficulty_config[2], PokemonFactory.pokemons, 2)

        elif sm.game_mode == "AIVSAI":
            if sm.current_ia_setup == 1:
                sm.difficulty_config[1] = level
                sm.current_ia_setup = 2
                sm.change_scene(SceneType.DIFFICULTY)
            else:
                sm.difficulty_config[2] = level
                bus_de_eventos_global.disparar("ESTABLECER_NUM_POKEMONES", 4)
                bus_de_eventos_global.disparar("ESTABLECER_JUGADOR_COMO_IA", 1, sm.difficulty_config[1], PokemonFactory.pokemons, 4) #El ultimo parametro es la profundidad de minimax si aplica
                bus_de_eventos_global.disparar("ESTABLECER_JUGADOR_COMO_IA", 2, sm.difficulty_config[2], PokemonFactory.pokemons, 4)
                bus_de_eventos_global.disparar("INICIALIZAR_COMBATE")

                sm.change_scene(SceneType.COMBAT)

    def draw(self, screen):
        for placeholder in self.placeholders:
            placeholder.draw(screen)

        current_option = list(self.buttons.keys())[self.selected_index]

        for option, button in self.buttons.items():
            button.draw(screen, option == current_option)
