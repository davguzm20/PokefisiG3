import pygame
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.scenes.enums.menu_option import MenuOption
from ui.components.button import Button
from ui.components.placeholder import Placeholder
from config.controls import Controls

class MenuScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 0
        self.buttons = {
            MenuOption.PLAY: Button(260, 282, 120, 44, "assets/ui/buttons/button-play.png", 20),
            MenuOption.RANKING: Button(480, 282, 120, 44, "assets/ui/buttons/button-ranking.png", 20),
            MenuOption.QUIT: Button(40, 282, 120, 44, "assets/ui/buttons/button-leave.png", 20),
        }
        self.placeholders = [
            Placeholder(0, 0, 640, 360, "assets/backgrounds/menus/fondo-campo.png"),
            Placeholder(110, 105, 420, 135, "assets/ui/titles/titulo-principal.png"),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == Controls.LEFT.value:
                self.selected_index = (self.selected_index - 1) % len(MenuOption)
            elif event.key == Controls.RIGHT.value:
                self.selected_index = (self.selected_index + 1) % len(MenuOption)
            elif event.key in Controls.SELECT.value:
                self.select_option()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for index, option in enumerate(self.buttons):
                    if self.buttons[option].is_selected(event.pos):
                        self.selected_index = index
                        self.select_option()

    def select_option(self):
        option = list(MenuOption)[self.selected_index]

        if option == MenuOption.PLAY:
            self.scene_manager.change_scene(SceneType.DIFFICULTY)
        elif option == MenuOption.RANKING:
            pass
        elif option == MenuOption.QUIT:
            pygame.event.post(pygame.Event(pygame.QUIT))

    def draw(self, screen):
        for placeholder in self.placeholders:
            placeholder.draw(screen)

        current_option = list(MenuOption)[self.selected_index]
        
        for option, button in self.buttons.items():
            button.draw(screen, option == current_option)
