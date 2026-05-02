import pygame

class Button:
    def __init__(self, position_x, position_y, width, height, text, text_size, normal_color, selected_color):
        self.position_x = position_x
        self.position_y = position_y
        self.width = width
        self.height = height
        self.text = text
        self.text_size = text_size
        self.normal_color = normal_color
        self.selected_color = selected_color
        self.rect = pygame.Rect(position_x, position_y, width, height)
    
    def draw(self, screen, is_selected):
        color = self.selected_color if is_selected else self.normal_color
        
        pygame.draw.rect(screen, color, self.rect, 2)
        
        font = pygame.font.Font(None, self.text_size)
        text_surface = font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_selected(self, mouse_position):
        return self.rect.collidepoint(mouse_position)