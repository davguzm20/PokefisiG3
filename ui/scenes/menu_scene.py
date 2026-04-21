import pygame
from ui.scenes.models.scene import Scene
from ui.scenes.enums.scene_type import SceneType
from ui.scenes.enums.menu_option import MenuOption
from ui.components.boton import Button
from config.colors import Colors
from config.controls import Controls

class MenuScene(Scene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self.selected_index = 0
        self.buttons = {
            MenuOption.PLAY: Button(250, 270, 300, 50, "JUGAR", 48, Colors.WHITE.value, Colors.GOLD.value),
            MenuOption.CONTROLS: Button(250, 330, 300, 50, "CONTROLES", 48, Colors.WHITE.value, Colors.GOLD.value),
            MenuOption.QUIT: Button(250, 390, 300, 50, "SALIR", 48, Colors.WHITE.value, Colors.GOLD.value),
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == Controls.UP.value:
                self.selected_index = (self.selected_index - 1) % 3
            elif event.key == Controls.DOWN.value:
                self.selected_index = (self.selected_index + 1) % 3
            elif event.key in Controls.SELECT.value:
                self.select_option()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for index, option in enumerate(MenuOption):
                    if self.buttons[option].is_selected(event.pos):
                        self.selected_index = index
                        self.select_option()

    def select_option(self):
        option = list(MenuOption)[self.selected_index]

        if option == MenuOption.PLAY:
            #self.scene_manager.change_scene(SceneType.TEAM)
            pass
        elif option == MenuOption.CONTROLS:
            pass
        elif option == MenuOption.QUIT:
            pygame.event.post(pygame.Event(pygame.QUIT))

    def draw(self, screen):
        screen.fill(Colors.DARK_GRAY.value)

        current_option = list(MenuOption)[self.selected_index]
        for option in MenuOption:
            self.buttons[option].draw(screen, option == current_option)