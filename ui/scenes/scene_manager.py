import pygame
from ui.scenes.enums.scene_type import SceneType
from ui.scenes.menu_scene import MenuScene
from ui.scenes.mode_scene import ModeScene
from ui.scenes.dificulty_scene import DifficultyScene
from ui.scenes.team_scene import TeamScene

class SceneManager:
    def __init__(self, screen):
        self.screen = screen
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
        self.current_scene = self.scenes[scene_type]

    def handle_event(self, event):
        self.current_scene.handle_event(event)
    
    def update(self):
        self.current_scene.update()
    
    def draw(self):
        self.current_scene.draw(self.screen)
    
    @staticmethod
    def run(juego=None):
        pygame.init()
        from config.settings import SCREEN_SIZE, CAPTION
        
        screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(CAPTION)
        
        manager = SceneManager(screen)
        manager.juego = juego
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                manager.handle_event(event)
            
            manager.update()
            manager.draw()
            pygame.display.flip()
        
        pygame.quit()