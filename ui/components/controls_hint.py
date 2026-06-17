import pygame
from ui.utils.fonts import Fonts
from config.colors import Colors


class ControlsHint:
    def __init__(self, show_left=True, show_right=True, show_up=False,
                 show_down=False, show_select=True, show_back=False,
                 select_label="SELECCIONAR", position_y=347,
                 show_click=False):
        self.show_left = show_left
        self.show_right = show_right
        self.show_up = show_up
        self.show_down = show_down
        self.show_select = show_select
        self.show_back = show_back
        self.select_label = select_label
        self.position_y = position_y
        self.show_click = show_click

    def draw(self, screen):
        parts = []
        arrows = []
        if self.show_up:
            arrows.append("^")
        if self.show_down:
            arrows.append("v")
        if self.show_left:
            arrows.append("<")
        if self.show_right:
            arrows.append(">")
        if arrows:
            parts.append(f"FLECHAS {'  '.join(arrows)} : MOVER")

        if self.show_select:
            select = "CLICK / " if self.show_click else ""
            select += f"ENTER / Z : {self.select_label}"
            parts.append(select)
        if self.show_back:
            parts.append("ESC / X : VOLVER")

        text = "               ".join(parts)

        font = Fonts.get_font(14)
        surface = font.render(text, False, Colors.WHITE.value)
        shadow = font.render(text, False, Colors.BLACK.value)
        text_rect = surface.get_rect(center=(320, self.position_y))
        screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
        screen.blit(surface, text_rect)
