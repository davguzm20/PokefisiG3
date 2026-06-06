import pygame
import random
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.components.placeholder import Placeholder
from ui.components.pokemon_layout import PokemonLayout
from ui.components.move_button import MoveButton
from ui.components.move_description import MoveDescription
from ui.components.health_bar import HealthBar
from config.controls import Controls
from config.colors import Colors
from pokemon.motor.bus_de_eventos import bus_de_eventos_global
from pokemon.motor.juego_interfaz import Acciones

class CombatScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 0
        self.showing_messages = False
        self._turn_count = 0
        self._is_ai_vs_ai = getattr(scene_manager, 'game_mode', None) == "AIVSAI"
        self._message_timer = 0
        self._game_over = False
        self._last_pop_time = 0
        self.acciones = Acciones()
        self.generando_acciones = False
        self.turno_terminado = False

        self.combat_messages = []
        bus_de_eventos_global.escuchar("MENSAJE_COMBATE", self.combat_messages.append)
        bus_de_eventos_global.escuchar("ELEGIR_INTERCAMBIO", self.elegir_intercambio)
        

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
        self.health_bars = [
            HealthBar(position_x=5, position_y=115),
            HealthBar(position_x=565, position_y=115),
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
        if not self.generando_acciones and not self.acciones.acciones_escogidas:
            bus_de_eventos_global.disparar("GENERAR_ACCIONES_IA", self.acciones, self.generando_acciones)
            self.generando_acciones = True      
            

        if event.type == pygame.KEYDOWN:
            if self._game_over:
                
                if event.key in Controls.SELECT.value and len(self.combat_messages) > 1:
                    now = pygame.time.get_ticks()
                    if now - self._last_pop_time > 500:
                        self.combat_messages.pop(0)
                        self._last_pop_time = now
                return

            if self.showing_messages:
                if event.key in Controls.SELECT.value:
                    now = pygame.time.get_ticks()
                    if now - self._last_pop_time < 500:
                        return
                    self._last_pop_time = now
                    self._release_hp_snapshot()
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
            if self._game_over:
                return
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
            for i, pokemon in enumerate([estado.pokemonActivoP1, estado.pokemonActivoP2]):
                self.health_bars[i].pokemon = pokemon
                if pokemon:
                    self.health_bars[i].display_hp = pokemon.hp
                    self.health_bars[i].display_max_hp = pokemon.current_hp

            self.acciones.acciones_escogidas = False
            self.generando_acciones = False # Creo que este es repetitivo pero no se si quitarlo

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
        juego = self.scene_manager.juego
        self.combat_messages.clear()

        for bar in self.health_bars:
            if bar.pokemon:
                bar.display_hp = bar.pokemon.hp
                bar.display_max_hp = bar.pokemon.current_hp

        #En vez de esperar que la IA genere las acciones lo mejor será que estas acciones ya hayan sido generadas.
        tick = 0
        while self.generando_acciones:
            if tick == 0:
                self.combat_messages.append("IA pensando...")
                tick += 1
            self.scene_manager.update()
            self.scene_manager.draw()
            pygame.display.flip()
            #print(self.acciones.accionP1, self.acciones.accionP2, self.acciones.acciones_escogidas)
            if self.acciones.acciones_escogidas:
                self.combat_messages.clear()
                self.generando_acciones = False

        if self._is_ai_vs_ai:
            accion_P1, accion_P2 = (self.acciones.accionP1, self.acciones.accionP2)
            
            for i, btn in enumerate(self.move_buttons):
                if btn.move == accion_P1:
                    self.selected_index = i
                    break
            game_over = juego.iniciar_turno(accionP1=accion_P1, accionP2=accion_P2)
        else:
            accion_P2 = self.acciones.accionP2
            move = self.move_buttons[self.selected_index].move
            game_over = juego.iniciar_turno(accionP1=move, accionP2=accion_P2)
        if game_over:
            self._game_over = True
        self._turn_count += 1
        self.turn_placeholder.label = f"Turno {self._turn_count}"
        self._message_timer = pygame.time.get_ticks() + 1500
        self.showing_messages = True

    def draw(self, screen):
        if self._is_ai_vs_ai:
            if self.showing_messages:
                if len(self.combat_messages) > 1 and self._message_timer and pygame.time.get_ticks() >= self._message_timer:
                    self._release_hp_snapshot()
                    self.combat_messages.pop(0)
                    self._message_timer = pygame.time.get_ticks() + 1500
                elif not self.combat_messages:
                    self.showing_messages = False
                    self._rebuild_pokemon_layout()
                    self._rebuild_move_buttons()
                    self._message_timer = pygame.time.get_ticks() + 1000
            elif not self._game_over:
                if self._message_timer == 0:
                    self._message_timer = pygame.time.get_ticks() + 1000
                elif pygame.time.get_ticks() >= self._message_timer:
                    self._message_timer = 0
                    self.select_move()

        for placeholder in self.placeholders:
            placeholder.draw(screen)

        for layout in self.pokemon_layouts:
            layout.draw(screen)

        for bar in self.health_bars:
            bar.draw(screen)

        for index, move_button in enumerate(self.move_buttons):
            move_button.draw(screen, is_selected=(index == self.selected_index))

        if self.combat_messages:
            self.move_description.label = self.combat_messages[0]
        else:
            self.move_description.label = ""
        self.move_description.draw(screen)
        self.turn_placeholder.draw(screen)
    
    #Elegibles es un arreglo de tuplas, donde cada tupla es (indice de pokemon en el equipo del jugador, referencia al pokemon)
    def _release_hp_snapshot(self):
        if self.combat_messages and "daño" in self.combat_messages[0]:
            for bar in self.health_bars:
                if hasattr(bar, 'display_hp'):
                    del bar.display_hp
                if hasattr(bar, 'display_max_hp'):
                    del bar.display_max_hp

    def elegir_intercambio(self, elegibles, idJugador):
        juego = self.scene_manager.juego

        #Esto ahora se maneja aleatoriamente pero debería manejarse usando la lista de elegibles en la interfaz para permitir al jugador elegir el nuevo indice/pokemon entrante
        idx_nuevo = random.choice(elegibles)[0]

        
        #=======================================
        juego.estado.intercambiarPokemon(idx_nuevo, idJugador)


