import pygame

from .. import ui
from .base import Game

CELL = 40
COLS, ROWS = ui.WIDTH // CELL, (ui.HEIGHT - 60) // CELL
DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


class Snake(Game):
    key = "snake"
    title = "Neon Snake"
    subtitle = "Eat, grow, don't bite yourself"
    color = (24, 150, 110)
    trophies = {"snake_10": "Hungry: eat 10 apples in one run"}

    def __init__(self, rng):
        super().__init__(rng)
        mid = (COLS // 2, ROWS // 2)
        self.body = [mid, (mid[0] - 1, mid[1]), (mid[0] - 2, mid[1])]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.timer = 0.0
        self.step = 0.11
        self.food = self._spawn_food()

    def _spawn_food(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in self.body]
        return self.rng.choice(free)

    def on_press(self, action):
        if action in DIRS:
            d = DIRS[action]
            if (d[0] + self.direction[0], d[1] + self.direction[1]) != (0, 0):
                self.next_direction = d

    def update(self, dt):
        if self.over:
            return
        self.timer += dt
        while self.timer >= self.step and not self.over:
            self.timer -= self.step
            self.direction = self.next_direction
            head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
            if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS) or head in self.body[:-1]:
                self.over = True
                return
            self.body.insert(0, head)
            if head == self.food:
                self.score += 1
                self.step = max(0.05, self.step * 0.97)
                if self.score >= 10:
                    self.award("snake_10")
                self.food = self._spawn_food()
            else:
                self.body.pop()

    def draw(self, surface):
        surface.fill((8, 14, 30))
        top = 60
        for x in range(COLS):
            for y in range(ROWS):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(surface, (12, 20, 42), (x * CELL, top + y * CELL, CELL, CELL))
        fx, fy = self.food
        pygame.draw.circle(surface, (235, 70, 90), (fx * CELL + CELL // 2, top + fy * CELL + CELL // 2), CELL // 2 - 6)
        for i, (x, y) in enumerate(self.body):
            shade = max(80, 220 - i * 6)
            pygame.draw.rect(surface, (40, shade, 150), (x * CELL + 3, top + y * CELL + 3, CELL - 6, CELL - 6), border_radius=10)
        self.draw_hud(surface, f"Length {len(self.body)}")

    def draw_icon(self, surface, rect):
        super().draw_icon(surface, rect)
        for i in range(5):
            pygame.draw.rect(surface, (120, 240, 190), (rect.x + 40 + i * 34, rect.centery - 15, 30, 30), border_radius=8)
        pygame.draw.circle(surface, (235, 70, 90), (rect.x + 250, rect.centery), 14)
