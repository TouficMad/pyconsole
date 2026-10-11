import pygame

from .. import ui


class Game:
    key = "game"
    title = "Game"
    subtitle = ""
    color = (40, 80, 160)
    # trophy id -> description
    trophies = {}

    def __init__(self, rng):
        self.rng = rng
        self.score = 0
        self.over = False
        self.earned = set()      # trophies unlocked during this run
        self.held = set()        # directions currently held down

    def press(self, action):
        self.held.add(action)
        self.on_press(action)

    def release(self, action):
        self.held.discard(action)

    def on_press(self, action):
        pass

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError

    def award(self, trophy):
        self.earned.add(trophy)

    def draw_icon(self, surface, rect):
        """Artwork for the home screen tile."""
        pygame.draw.rect(surface, self.color, rect, border_radius=18)

    def draw_hud(self, surface, extra=""):
        ui.text(surface, f"{self.title}   Score {self.score}   {extra}", 24, (24, 16), ui.WHITE, bold=True)
