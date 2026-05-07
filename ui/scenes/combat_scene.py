import pygame
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.components.placeholder import Placeholder
from ui.components.pokemon_layout import PokemonLayout
from ui.components.move_button import MoveButton
from config.controls import Controls

class CombatScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 0
        self.placeholders = [
            Placeholder(
                position_x=0, position_y=0,
                width=640, height=360,
                asset="assets/backgrounds/menus/fondo-banderas.png",
            ),
        ]
        self.pokemon_layouts = [
            PokemonLayout(position_x=125, position_y=75, number_player=1),
            PokemonLayout(position_x=350, position_y=50, number_player=2),
        ]

        moves = []
        juego = scene_manager.juego

        if juego and juego.combate:
            estado = juego.get_combate().estado_del_equipo

            if estado.pokemonActivoP1:
                moves = estado.pokemonActivoP1.moves[:4]

        columns = 2
        column_gap = 25
        row_gap = 15
        total_width = columns * 150 + (columns - 1) * column_gap
        start_x = (640 - total_width) // 2
        start_y = 360 - 50 * 2 - row_gap - 10

        self.move_buttons = [
            MoveButton(
                position_x=start_x + (index % columns) * (150 + column_gap),
                position_y=start_y + (index // columns) * (50 + row_gap),
                move=move,
            )
            for index, move in enumerate(moves)
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == Controls.LEFT.value:
                if self.move_buttons:
                    self.selected_index = (self.selected_index - 1) % len(self.move_buttons)
            elif event.key == Controls.RIGHT.value:
                if self.move_buttons:
                    self.selected_index = (self.selected_index + 1) % len(self.move_buttons)
            elif event.key == Controls.UP.value:
                if self.move_buttons and self.selected_index >= 2:
                    self.selected_index -= 2
            elif event.key == Controls.DOWN.value:
                if self.move_buttons:
                    new_index = self.selected_index + 2
                    if new_index < len(self.move_buttons):
                        self.selected_index = new_index
            elif event.key in Controls.SELECT.value:
                if self.move_buttons:
                    self.select_move()
            elif event.key in Controls.BACK.value:
                self.scene_manager.change_scene(SceneType.MENU)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, move_button in enumerate(self.move_buttons):
                if move_button.is_selected(event.pos):
                    self.selected_index = index
                    self.select_move()

    def select_move(self):
        move_button = self.move_buttons[self.selected_index]
        if move_button.on_click:
            move_button.on_click()

    def draw(self, screen):
        for placeholder in self.placeholders:
            placeholder.draw(screen)

        juego = self.scene_manager.juego

        if juego and juego.combate:
            estado = juego.get_combate().estado_del_equipo
            self.pokemon_layouts[0].pokemon = estado.pokemonActivoP1
            self.pokemon_layouts[1].pokemon = estado.pokemonActivoP2

        for layout in self.pokemon_layouts:
            layout.draw(screen)

        for index, move_button in enumerate(self.move_buttons):
            move_button.draw(screen, is_selected=(index == self.selected_index))
