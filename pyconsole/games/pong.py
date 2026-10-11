import pygame

from .. import ui
from .base import Game

PADDLE_W, PADDLE_H, BALL = 16, 110, 16
WIN_SCORE = 7


class Pong(Game):
    key = "pong"
    title = "Hyper Pong"
    subtitle = "First to 7 against the CPU"
    color = (130, 60, 200)
    trophies = {"pong_win": "Champion: beat the CPU at Hyper Pong"}

    def __init__(self, rng):
        super().__init__(rng)
        self.player_y = self.cpu_y = ui.HEIGHT / 2 - PADDLE_H / 2
        self.cpu_score = 0
        self._serve(direction=1)

    def _serve(self, direction):
        self.ball = pygame.Vector2(ui.WIDTH / 2, ui.HEIGHT / 2)
        angle = self.rng.uniform(-0.6, 0.6)
        self.vel = pygame.Vector2(direction * 520, 0).rotate_rad(angle)

    def update(self, dt):
        if self.over:
            return
        speed = 620 * dt
        if "up" in self.held:
            self.player_y -= speed
        if "down" in self.held:
            self.player_y += speed
        # the CPU follows the ball, a little slower than the player can move
        target = self.ball.y - PADDLE_H / 2
        self.cpu_y += max(-430 * dt, min(430 * dt, target - self.cpu_y))
        self.player_y = max(60, min(ui.HEIGHT - PADDLE_H, self.player_y))
        self.cpu_y = max(60, min(ui.HEIGHT - PADDLE_H, self.cpu_y))

        self.ball += self.vel * dt
        if self.ball.y < 60 or self.ball.y > ui.HEIGHT - BALL:
            self.vel.y *= -1
            self.ball.y = max(60, min(ui.HEIGHT - BALL, self.ball.y))

        ball = pygame.Rect(self.ball.x, self.ball.y, BALL, BALL)
        player = pygame.Rect(40, self.player_y, PADDLE_W, PADDLE_H)
        cpu = pygame.Rect(ui.WIDTH - 40 - PADDLE_W, self.cpu_y, PADDLE_W, PADDLE_H)
        for paddle, direction in ((player, 1), (cpu, -1)):
            if ball.colliderect(paddle) and self.vel.x * direction < 0:
                offset = (ball.centery - paddle.centery) / (PADDLE_H / 2)
                self.vel = pygame.Vector2(direction * min(abs(self.vel.x) * 1.06, 1100), offset * 420)

        if self.ball.x < 0:
            self.cpu_score += 1
            self._serve(direction=1)
        elif self.ball.x > ui.WIDTH:
            self.score += 1
            self._serve(direction=-1)
        if self.score >= WIN_SCORE:
            self.award("pong_win")
            self.over = True
        elif self.cpu_score >= WIN_SCORE:
            self.over = True

    def draw(self, surface):
        surface.fill((14, 8, 30))
        for y in range(70, ui.HEIGHT, 40):
            pygame.draw.rect(surface, (60, 40, 100), (ui.WIDTH // 2 - 3, y, 6, 20))
        ui.text(surface, f"{self.score}   {self.cpu_score}", 64, (ui.WIDTH // 2, 120), (200, 170, 255), bold=True, center=True)
        pygame.draw.rect(surface, (220, 200, 255), (40, self.player_y, PADDLE_W, PADDLE_H), border_radius=6)
        pygame.draw.rect(surface, (255, 120, 160), (ui.WIDTH - 40 - PADDLE_W, self.cpu_y, PADDLE_W, PADDLE_H), border_radius=6)
        pygame.draw.rect(surface, ui.WHITE, (self.ball.x, self.ball.y, BALL, BALL), border_radius=8)
        self.draw_hud(surface, "You vs CPU")

    def draw_icon(self, surface, rect):
        super().draw_icon(surface, rect)
        pygame.draw.rect(surface, ui.WHITE, (rect.x + 40, rect.centery - 45, 14, 90), border_radius=5)
        pygame.draw.rect(surface, ui.WHITE, (rect.right - 54, rect.centery - 20, 14, 90), border_radius=5)
        pygame.draw.circle(surface, ui.WHITE, (rect.centerx + 20, rect.centery - 10), 11)
