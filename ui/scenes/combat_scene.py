import pygame
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.components.placeholder import Placeholder
from ui.components.pokemon_layout import PokemonLayout
from config.controls import Controls

class CombatScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.placeholders = [
            Placeholder(
                position_x=0, position_y=0,
                width=640, height=360,
                asset="assets/backgrounds/menus/fondo-banderas.png",
            ),
        ]
        self.pokemonLayouts = [
            PokemonLayout(position_x=125, position_y=75, number_player=1),
            PokemonLayout(position_x=350, position_y=50, number_player=2),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in Controls.BACK.value:
                self.scene_manager.change_scene(SceneType.MENU)

    def draw(self, screen):
        for placeholder in self.placeholders:
            placeholder.draw(screen)

        juego = self.scene_manager.juego

        if juego and juego.combate:
            estado = juego.get_combate().estado_del_equipo
            self.pokemonLayouts[0].pokemon = estado.pokemonActivoP1
            self.pokemonLayouts[1].pokemon = estado.pokemonActivoP2

        for layout in self.pokemonLayouts:
            layout.draw(screen)
