import pygame
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.scenes.enums.difficulty_option import DifficultyOption
from ui.components.button import Button
from ui.components.placeholder import Placeholder
from config.controls import Controls

class DifficultyScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 1
        self.buttons = {
            DifficultyOption.EASY: Button(40, 282, 120, 44, "assets/ui/buttons/button-easy.png", 20),
            DifficultyOption.INTERMEDIATE: Button(260, 282, 120, 44, "assets/ui/buttons/button-intermediate.png", 20),
            DifficultyOption.HARD: Button(480, 282, 120, 44, "assets/ui/buttons/button-hard.png", 20),
        }
        self.placeholders = [
            Placeholder(0, 0, 640, 360, "assets/backgrounds/menus/fondo-campo.png"),
            Placeholder(110, 105, 420, 135, "assets/ui/titles/titulo-principal.png"),
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
                self.scene_manager.change_scene(SceneType.MENU)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for index, option in enumerate(self.buttons):
                    if self.buttons[option].is_selected(event.pos):
                        self.selected_index = index
                        self.select_option()

    def select_option(self):
        option = list(self.buttons.keys())[self.selected_index]

        if option == DifficultyOption.EASY:
            self.scene_manager.change_scene(SceneType.TEAM)
        elif option == DifficultyOption.INTERMEDIATE:
            self.scene_manager.change_scene(SceneType.TEAM)
        elif option == DifficultyOption.HARD:
            self.scene_manager.change_scene(SceneType.TEAM)

    def draw(self, screen):
        for placeholder in self.placeholders:
            placeholder.draw(screen)

        current_option = list(self.buttons.keys())[self.selected_index]
        
        for option, button in self.buttons.items():
            button.draw(screen, option == current_option)
