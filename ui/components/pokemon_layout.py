import pygame
from ui.utils.assets import Assets
from pokemon.models.pokemon import Pokemon


class PokemonLayout:
    SIZE = 180
    SCALE = 2

    def __init__(self, position_x: int, position_y: int,
                 pokemon: Pokemon | None = None, number_player: int = 1):
        self.position_x = position_x
        self.position_y = position_y
        self.pokemon = pokemon
        self.number_player = number_player
        self.frames = []
        self.frame_index = 0
        self.last_frame_time = 0
        self.flash_until = 0
        self.faint_start = None
        self.faint_duration = 600
        self.fainted = False

    def rebuild(self):
        self.frames = []
        self.frame_index = 0
        self.faint_start = None
        self.fainted = False

    def flash(self, duration=350):
        self.flash_until = pygame.time.get_ticks() + duration

    def start_faint(self):
        self.faint_start = pygame.time.get_ticks()

    def draw(self, screen):
        if self.pokemon:
            if not self.frames:
                if self.number_player == 1:
                    sprite_path = self.pokemon.sprites.back
                else:
                    sprite_path = self.pokemon.sprites.regular

                frames_data = Assets.load_gif(sprite_path)

                if frames_data:
                    first_frame = frames_data[0][0]
                    sprite_width = int(first_frame.get_width() * self.SCALE)
                    sprite_height = int(first_frame.get_height() * self.SCALE)
                    position_x = self.position_x + (self.SIZE - sprite_width) // 2
                    position_y = self.position_y + self.SIZE - sprite_height

                    for surface, duration in frames_data:
                        scaled_surface = pygame.transform.scale(surface, (sprite_width, sprite_height))
                        scaled_surface = pygame.transform.flip(scaled_surface, False, False)
                        self.frames.append((scaled_surface, duration, position_x, position_y, sprite_width, sprite_height))

                    self.last_frame_time = pygame.time.get_ticks()

            if self.frames:
                now = pygame.time.get_ticks()
                current_frame = self.frames[self.frame_index]

                if now - self.last_frame_time >= current_frame[1]:
                    self.frame_index = (self.frame_index + 1) % len(self.frames)
                    self.last_frame_time = now
                    current_frame = self.frames[self.frame_index]

                if self.fainted:
                    return

                surface = current_frame[0]
                pos = (current_frame[2], current_frame[3])

                if self.faint_start is not None:
                    elapsed = now - self.faint_start
                    progress = min(elapsed / self.faint_duration, 1.0)
                    scale_x = 1.0 + progress * 0.15
                    scale_y = 1.0 - progress
                    w = max(1, int(surface.get_width() * scale_x))
                    h = max(1, int(surface.get_height() * scale_y))
                    surface = pygame.transform.scale(surface, (w, h))
                    surface.set_alpha(int(255 * (1 - progress)))
                    pos = (
                        current_frame[2] - (w - current_frame[4]) // 2,
                        current_frame[3] + (current_frame[5] - h),
                    )
                    if progress >= 1.0:
                        self.fainted = True
                        self.faint_start = None
                        return

                screen.blit(surface, pos)

                if self.flash_until > now:
                    flash_surf = current_frame[0].copy()
                    flash_surf.fill((255, 0, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                    flash_surf.set_alpha(220)
                    screen.blit(flash_surf, pos)
