import pygame
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.scenes.enums.mode_option import ModeOption
from ui.components.button import Button
from ui.components.placeholder import Placeholder
from ui.components.controls_hint import ControlsHint
from config.colors import Colors
from config.controls import Controls

class ModeScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 0
        self.buttons = {
            ModeOption.VS_CPU: Button(
                position_x=100, position_y=282,
                width=200, height=44,
                label="JUGADOR VS IA",
                text_size=18,
                background_color=Colors.BLUE,
            ),
            ModeOption.CPU_VS_CPU: Button(
                position_x=340, position_y=282,
                width=200, height=44,
                label="IA VS IA",
                text_size=18,
                background_color=Colors.BLUE,
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
        self.controls_hint = ControlsHint(show_back=True, show_click=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == Controls.LEFT.value:
                self.selected_index = (self.selected_index - 1) % len(ModeOption)
            elif event.key == Controls.RIGHT.value:
                self.selected_index = (self.selected_index + 1) % len(ModeOption)
            elif event.key in Controls.SELECT.value:
                self.select_option()
            elif event.key in Controls.BACK.value:
                self.scene_manager.change_scene(SceneType.MENU)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, option in enumerate(self.buttons):
                if self.buttons[option].is_selected(event.pos):
                    self.selected_index = index
                    self.select_option()

    def select_option(self):
        option = list(ModeOption)[self.selected_index]

        if option == ModeOption.VS_CPU:
            self.scene_manager.game_mode = "PVAI"
        elif option == ModeOption.CPU_VS_CPU:
            self.scene_manager.game_mode = "AIVSAI"

        self.scene_manager.current_ia_setup = 1
        self.scene_manager.difficulty_config = {}
        self.scene_manager.change_scene(SceneType.DIFFICULTY)

    def draw(self, screen):
        for placeholder in self.placeholders:
            placeholder.draw(screen)

        current_option = list(ModeOption)[self.selected_index]

        for option, button in self.buttons.items():
            button.draw(screen, option == current_option)

        self.controls_hint.draw(screen)
