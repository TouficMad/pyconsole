import pygame

from .. import ui
from .base import Game

ROWS, COLS = 6, 12
BRICK_W, BRICK_H = ui.WIDTH // COLS, 30
COLORS = [(235, 80, 90), (240, 140, 60), (240, 200, 60), (90, 200, 120), (60, 160, 230), (150, 100, 230)]


class Breakout(Game):
    key = "breakout"
    title = "Brick Breaker"
    subtitle = "Clear the wall, 3 lives"
    color = (200, 90, 40)
    trophies = {"breakout_clear": "Demolition: clear every brick"}

    def __init__(self, rng):
        super().__init__(rng)
        self.bricks = [pygame.Rect(c * BRICK_W + 2, 110 + r * BRICK_H + 2, BRICK_W - 4, BRICK_H - 4)
                       for r in range(ROWS) for c in range(COLS)]
        self.brick_colors = {id(b): COLORS[i // COLS] for i, b in enumerate(self.bricks)}
        self.paddle = pygame.Rect(ui.WIDTH // 2 - 80, ui.HEIGHT - 50, 160, 16)
        self.lives = 3
        self._reset_ball()

    def _reset_ball(self):
        self.ball = pygame.Vector2(self.paddle.centerx, self.paddle.top - 20)
        self.vel = pygame.Vector2(self.rng.choice([-1, 1]) * 260, -420)

    def update(self, dt):
        if self.over:
            return
        if "left" in self.held:
            self.paddle.x -= int(760 * dt)
        if "right" in self.held:
            self.paddle.x += int(760 * dt)
        self.paddle.clamp_ip(pygame.Rect(0, 0, ui.WIDTH, ui.HEIGHT))

        self.ball += self.vel * dt
        if self.ball.x < 8 or self.ball.x > ui.WIDTH - 8:
            self.vel.x *= -1
            self.ball.x = max(8, min(ui.WIDTH - 8, self.ball.x))
        if self.ball.y < 68:
            self.vel.y = abs(self.vel.y)
        ball = pygame.Rect(self.ball.x - 8, self.ball.y - 8, 16, 16)
        if ball.colliderect(self.paddle) and self.vel.y > 0:
            offset = (ball.centerx - self.paddle.centerx) / (self.paddle.width / 2)
            self.vel = pygame.Vector2(offset * 420, -abs(self.vel.y))
        hit = ball.collidelist(self.bricks)
        if hit != -1:
            self.bricks.pop(hit)
            self.vel.y *= -1
            self.score += 10
            if not self.bricks:
                self.award("breakout_clear")
                self.over = True
        if self.ball.y > ui.HEIGHT:
            self.lives -= 1
            if self.lives == 0:
                self.over = True
            else:
                self._reset_ball()

    def draw(self, surface):
        surface.fill((20, 10, 8))
        for brick in self.bricks:
            pygame.draw.rect(surface, self.brick_colors[id(brick)], brick, border_radius=6)
        pygame.draw.rect(surface, ui.WHITE, self.paddle, border_radius=8)
        pygame.draw.circle(surface, (255, 230, 180), self.ball, 8)
        self.draw_hud(surface, f"Lives {self.lives}")

    def draw_icon(self, surface, rect):
        super().draw_icon(surface, rect)
        for r in range(3):
            for c in range(5):
                pygame.draw.rect(surface, COLORS[r * 2], (rect.x + 30 + c * 52, rect.y + 40 + r * 26, 46, 20), border_radius=5)
        pygame.draw.rect(surface, ui.WHITE, (rect.centerx - 50, rect.bottom - 40, 100, 12), border_radius=5)
        pygame.draw.circle(surface, ui.WHITE, (rect.centerx + 30, rect.bottom - 70), 9)
