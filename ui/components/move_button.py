import pygame
from pokemon.models.move import Move
from config.colors import Colors
from ui.utils.assets import Assets
from ui.utils.fonts import Fonts
from ui.components.button import Button


class MoveButton(Button):
    WIDTH = 165
    HEIGHT = 50

    def __init__(self, position_x: int, position_y: int, move: Move,
                 on_click=None, selected_color: Colors = Colors.GOLD,
                 border_size: int = 3):
        super().__init__(
            position_x=position_x,
            position_y=position_y,
            width=self.WIDTH,
            height=self.HEIGHT,
            selected_color=selected_color,
            border_size=border_size,
        )
        self.move = move
        self.on_click = on_click

    def draw(self, screen, is_selected=False):
        rect = pygame.Rect(self.position_x, self.position_y, self.width, self.height)
        move_type_name = self.move.type.name.lower()

        background_surface = Assets.load_image(
            f"assets/ui/frames/types/cuadro-ataque-{move_type_name}.png",
            self.width, self.height,
        )
        big_type_icon = Assets.load_image(f"assets/ui/type-icons/icon-type-{move_type_name}.png")
        mini_type_icon = Assets.load_image(f"assets/ui/type-mini/{move_type_name}.png")
        move_class_icon = Assets.load_image(
            f"assets/ui/move-class-icons/{self.move.damage_class.name.lower()}.png"
        )

        text_font = Fonts.get_font(16)
        move_name_text = self.move.name.upper()

        name_text_surface = text_font.render(move_name_text, False, Colors.WHITE.value)
        name_shadow = text_font.render(move_name_text, False, Colors.BLACK.value)
        pp_text_surface = text_font.render(
            f"PP {self.move.current_power_points}/{self.move.power_points}",
            False, Colors.WHITE.value,
        )
        pp_shadow = text_font.render(
            f"PP {self.move.current_power_points}/{self.move.power_points}",
            False, Colors.BLACK.value,
        )

        if background_surface:
            screen.blit(background_surface, (self.position_x, self.position_y))

        mini_column_width = max(
            mini_type_icon.get_width() if mini_type_icon else 0,
            move_class_icon.get_width() if move_class_icon else 0,
        )
        mini_column_height = 0
        if mini_type_icon:
            mini_column_height = mini_type_icon.get_height()
        if move_class_icon:
            mini_column_height += 2 + move_class_icon.get_height()

        if big_type_icon and mini_column_height > 0:
            scale_factor = mini_column_height / big_type_icon.get_height()
            new_big_width = int(big_type_icon.get_width() * scale_factor)
            big_type_icon = pygame.transform.scale(big_type_icon, (new_big_width, mini_column_height))

        big_icon_width = big_type_icon.get_width() if big_type_icon else 0
        big_icon_height = big_type_icon.get_height() if big_type_icon else 0
        text_block_width = max(name_text_surface.get_width(), pp_text_surface.get_width())
        gap_big_to_mini = 4
        gap_mini_to_text = 4
        total_width = big_icon_width + gap_big_to_mini + mini_column_width + gap_mini_to_text + text_block_width
        group_start_x = self.position_x + (self.width - total_width) // 2

        if big_type_icon:
            big_icon_position_y = self.position_y + (self.height - big_icon_height) // 2
            screen.blit(big_type_icon, (group_start_x, big_icon_position_y))

        mini_column_start_x = group_start_x + big_icon_width + gap_big_to_mini

        if mini_type_icon:
            mini_type_icon_y = self.position_y + (self.height - mini_column_height) // 2
            screen.blit(mini_type_icon, (mini_column_start_x, mini_type_icon_y))
        else:
            mini_type_icon_y = self.position_y + (self.height - mini_column_height) // 2

        if move_class_icon:
            if mini_type_icon:
                class_icon_y = mini_type_icon_y + mini_type_icon.get_height() + 2
            else:
                class_icon_y = self.position_y + (self.height - move_class_icon.get_height()) // 2

            screen.blit(move_class_icon, (mini_column_start_x, class_icon_y))

        text_block_start_x = mini_column_start_x + mini_column_width + gap_mini_to_text
        text_block_height = name_text_surface.get_height() + 2 + pp_text_surface.get_height()
        name_text_position_y = self.position_y + (self.height - text_block_height) // 2
        pp_text_position_y = name_text_position_y + name_text_surface.get_height() + 2

        screen.blit(name_shadow, (text_block_start_x + 1, name_text_position_y + 1))
        screen.blit(name_text_surface, (text_block_start_x, name_text_position_y))
        screen.blit(pp_shadow, (text_block_start_x + 1, pp_text_position_y + 1))
        screen.blit(pp_text_surface, (text_block_start_x, pp_text_position_y))

        if is_selected:
            pygame.draw.rect(screen, self.selected_color.value, rect, self.border_size)
