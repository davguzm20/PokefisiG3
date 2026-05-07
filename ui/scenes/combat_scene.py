import pygame
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.components.placeholder import Placeholder
from ui.components.pokemon_layout import PokemonLayout
from ui.components.move_button import MoveButton
from ui.components.move_description import MoveDescription
from config.controls import Controls
from config.colors import Colors
from pokemon.motor.bus_de_eventos import bus_de_eventos_global

class CombatScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 0
        self.showing_messages = False
        self._turn_count = 0

        self.combat_messages = []
        bus_de_eventos_global.escuchar("MENSAJE_COMBATE", self.combat_messages.append)
        
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

        self._button_columns = 2
        self._button_gap_x = 25
        self._button_gap_y = 10
        self._button_total_width = self._button_columns * 150 + (self._button_columns - 1) * self._button_gap_x
        self._button_start_x = (640 - self._button_total_width) // 2
        self._button_start_y = 360 - 50 * 2 - self._button_gap_y - 10

        self._rebuild_pokemon_layout()
        self._rebuild_move_buttons()

        self.move_description = MoveDescription(
            position_y=20,
            text="",
        )

        move_description_x = (640 - MoveDescription.WIDTH) // 2
        self.turn_placeholder = Placeholder(
            position_x=move_description_x + MoveDescription.WIDTH + 10,
            position_y=20,
            width=100,
            height=35,
            asset="assets/ui/frames/cuadro-turno.png",
            text_color=Colors.WHITE,
            text_size=16,
            label="",
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.showing_messages:
                if event.key in Controls.SELECT.value:
                    if self.combat_messages:
                        self.combat_messages.pop(0)
                    if not self.combat_messages:
                        self.showing_messages = False
                        self._rebuild_pokemon_layout()
                        self._rebuild_move_buttons()
                return

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
            if self.showing_messages:
                return
            for index, move_button in enumerate(self.move_buttons):
                if move_button.is_selected(event.pos):
                    self.selected_index = index
                    self.select_move()

    def _rebuild_pokemon_layout(self):
        juego = self.scene_manager.juego
        if juego and juego.combate:
            estado = juego.get_combate().estado_del_equipo
            self.pokemon_layouts[0].pokemon = estado.pokemonActivoP1
            self.pokemon_layouts[1].pokemon = estado.pokemonActivoP2
        for layout in self.pokemon_layouts:
            layout.rebuild()

    def _rebuild_move_buttons(self):
        juego = self.scene_manager.juego
        moves = []
        if juego and juego.combate:
            estado = juego.get_combate().estado_del_equipo
            if estado.pokemonActivoP1:
                moves = estado.pokemonActivoP1.moves[:4]
        self.move_buttons = [
            MoveButton(
                position_x=self._button_start_x + (i % self._button_columns) * (150 + self._button_gap_x),
                position_y=self._button_start_y + (i // self._button_columns) * (50 + self._button_gap_y),
                move=move,
            )
            for i, move in enumerate(moves)
        ]
        self.selected_index = 0

    def select_move(self):
        move = self.move_buttons[self.selected_index].move
        juego = self.scene_manager.juego
        juego.iniciar_turno(accionP1=move)
        self._turn_count += 1
        self.turn_placeholder.label = f"Turno {self._turn_count}"
        self.showing_messages = True

    def draw(self, screen):
        for placeholder in self.placeholders:
            placeholder.draw(screen)

        for layout in self.pokemon_layouts:
            layout.draw(screen)

        for index, move_button in enumerate(self.move_buttons):
            move_button.draw(screen, is_selected=(index == self.selected_index))

        if self.showing_messages and self.combat_messages:
            self.move_description.label = self.combat_messages[0]
        else:
            self.move_description.label = ""
        self.move_description.draw(screen)
        self.turn_placeholder.draw(screen)
