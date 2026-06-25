import pygame
import ctypes
from config.settings import BASE_WIDTH, BASE_HEIGHT, SCREEN_SIZE, CAPTION
from ui.scenes.enums.scene_type import SceneType
from ui.scenes.menu_scene import MenuScene
from ui.scenes.mode_scene import ModeScene
from ui.scenes.difficulty_scene import DifficultyScene
from ui.scenes.team_scene import TeamScene
from ui.scenes.combat_scene import CombatScene

class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.render_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        self.juego = None
        self.game_mode = None
        self.current_ia_setup = 1
        self.difficulty_config = {}
        self.scenes = {
            SceneType.MENU: MenuScene(self),
            SceneType.MODE: ModeScene(self),
            SceneType.DIFFICULTY: DifficultyScene(self),
            SceneType.TEAM: TeamScene(self),
        }
        self.current_scene = self.scenes[SceneType.MENU]

    def change_scene(self, scene_type: SceneType):
        if hasattr(self.current_scene, 'on_exit'):
            self.current_scene.on_exit()
        if scene_type == SceneType.COMBAT:
            self.current_scene = CombatScene(self)
        else:
            self.current_scene = self.scenes[scene_type]

    def _get_scale_info(self):
        win_w, win_h = self.screen.get_size()
        scale = min(win_w / BASE_WIDTH, win_h / BASE_HEIGHT)
        scaled_w = int(BASE_WIDTH * scale)
        scaled_h = int(BASE_HEIGHT * scale)
        offset_x = (win_w - scaled_w) // 2
        offset_y = (win_h - scaled_h) // 2
        return scale, offset_x, offset_y, scaled_w, scaled_h

    def _to_render_coords(self, pos):
        scale, offset_x, offset_y, _, _ = self._get_scale_info()
        x = int((pos[0] - offset_x) / scale)
        y = int((pos[1] - offset_y) / scale)
        return (x, y)

    def handle_event(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            translated = self._to_render_coords(event.pos)
            event = pygame.event.Event(event.type, {
                'pos': translated, 'button': event.button
            })
        elif event.type == pygame.MOUSEMOTION:
            translated = self._to_render_coords(event.pos)
            event = pygame.event.Event(event.type, {
                'pos': translated, 'rel': event.rel, 'buttons': event.buttons
            })
        self.current_scene.handle_event(event)
    
    def update(self):
        self.current_scene.update()
    
    def draw(self):
        self.render_surface.fill((0, 0, 0))
        self.current_scene.draw(self.render_surface)
        _, offset_x, offset_y, scaled_w, scaled_h = self._get_scale_info()
        scaled = pygame.transform.scale(self.render_surface, (scaled_w, scaled_h))
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, (offset_x, offset_y))
    
    @staticmethod
    def _maximize_window():
        try:
            hwnd = pygame.display.get_wm_info()["window"]
            ctypes.windll.user32.ShowWindow(hwnd, 3)
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
            new_w = rect.right - rect.left
            new_h = rect.bottom - rect.top
            return pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
        except Exception:
            return None

    @staticmethod
    def run(juego=None):
        pygame.init()
        
        screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(CAPTION)

        maximized = SceneManager._maximize_window()
        if maximized:
            screen = maximized
        
        manager = SceneManager(screen)
        manager.juego = juego
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    manager.screen = screen
                manager.handle_event(event)
            
            manager.update()
            manager.draw()
            pygame.display.flip()
        
        pygame.quit()