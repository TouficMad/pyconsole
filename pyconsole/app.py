"""The console: boot animation, home screen, game sessions, pause menu and trophies."""
import math
import random
import time

import pygame

from . import ui
from .games import GAMES
from .storage import SaveData

KEYMAP = {
    pygame.K_UP: "up", pygame.K_w: "up",
    pygame.K_DOWN: "down", pygame.K_s: "down",
    pygame.K_LEFT: "left", pygame.K_a: "left",
    pygame.K_RIGHT: "right", pygame.K_d: "right",
    pygame.K_RETURN: "confirm", pygame.K_SPACE: "confirm",
    pygame.K_ESCAPE: "back", pygame.K_BACKSPACE: "back",
}
# common gamepad layout: 0 = cross/A, 1 = circle/B, 7 or 9 = options/start
PAD_BUTTONS = {0: "confirm", 1: "back", 7: "back", 9: "back"}
PLATINUM = "platinum"
TROPHY_NAMES = {PLATINUM: "Platinum: unlock every other trophy"}
for _g in GAMES:
    TROPHY_NAMES.update(_g.trophies)

TILE_W, TILE_H, TILE_GAP = 320, 200, 36


class Console:
    def __init__(self, surface, save=None, rng=None):
        self.surface = surface
        self.save = save or SaveData()
        self.rng = rng or random.Random()
        self.state = "boot"
        self.t = 0.0
        self.selected = 0
        self.scroll = 0.0
        self.game = None
        self.paused = False
        self.pause_choice = 0
        self.toasts = []          # [text, seconds left]
        self.items = [g for g in GAMES] + ["trophies"]
        self.running = True

    # ---------- input ----------
    def press(self, action):
        if self.state == "boot":
            self.state = "home"
        elif self.state == "home":
            self._home_input(action)
        elif self.state == "trophies":
            if action in ("back", "confirm"):
                self.state = "home"
        elif self.state == "game":
            self._game_input(action)

    def release(self, action):
        if self.state == "game" and self.game:
            self.game.release(action)

    def _home_input(self, action):
        if action == "left":
            self.selected = max(0, self.selected - 1)
        elif action == "right":
            self.selected = min(len(self.items) - 1, self.selected + 1)
        elif action == "confirm":
            item = self.items[self.selected]
            if item == "trophies":
                self.state = "trophies"
            else:
                self.game = item(self.rng)
                self.paused = False
                self.state = "game"

    def _game_input(self, action):
        if self.game.over:
            if action in ("confirm", "back"):
                self.state = "home"
                self.game = None
            return
        if self.paused:
            if action in ("up", "down"):
                self.pause_choice = 1 - self.pause_choice
            elif action == "confirm":
                if self.pause_choice == 0:
                    self.paused = False
                else:
                    self._finish_game()
                    self.state, self.game = "home", None
            elif action == "back":
                self.paused = False
            return
        if action == "back":
            self.paused, self.pause_choice = True, 0
        else:
            self.game.press(action)

    # ---------- logic ----------
    def update(self, dt):
        self.t += dt
        if self.state == "boot" and self.t > 3.2:
            self.state = "home"
        self.scroll += (self.selected - self.scroll) * min(1, dt * 10)
        if self.state == "game" and self.game and not self.paused and not self.game.over:
            self.game.update(dt)
            self._collect_trophies()
            if self.game.over:
                self._finish_game()
        for toast in self.toasts:
            toast[1] -= dt
        self.toasts = [t for t in self.toasts if t[1] > 0]

    def _collect_trophies(self):
        for trophy in list(self.game.earned):
            if self.save.unlock(trophy):
                self.toasts.append([f"Trophy unlocked: {TROPHY_NAMES[trophy]}", 4.0])
        game_trophies = set(TROPHY_NAMES) - {PLATINUM}
        if game_trophies <= self.save.trophies and self.save.unlock(PLATINUM):
            self.toasts.append([f"Trophy unlocked: {TROPHY_NAMES[PLATINUM]}", 5.0])

    def _finish_game(self):
        if self.game and self.save.record_score(self.game.key, self.game.score) and self.game.score > 0:
            self.toasts.append([f"New high score in {self.game.title}: {self.game.score}", 4.0])

    # ---------- drawing ----------
    def draw(self):
        s = self.surface
        if self.state == "boot":
            self._draw_boot(s)
        elif self.state == "home":
            self._draw_home(s)
        elif self.state == "trophies":
            self._draw_trophies(s)
        elif self.state == "game":
            self.game.draw(s)
            if self.paused:
                self._draw_pause(s)
            elif self.game.over:
                self._draw_game_over(s)
        self._draw_toasts(s)

    def _draw_boot(self, s):
        s.fill((0, 0, 0))
        p = min(1, self.t / 1.5)
        cx, cy = ui.WIDTH // 2, ui.HEIGHT // 2 - 30
        # original logo: three rings expanding into place around a play arrow
        for i in range(3):
            a = max(0, min(1, (self.t - i * 0.3) / 0.7))
            col = [int(c * a) for c in (90, 160, 255)]
            pygame.draw.circle(s, col, (cx, cy), int(30 + 22 * i * a), 4)
        a = max(0, min(1, (self.t - 0.9) / 0.5))
        pygame.draw.polygon(s, [int(255 * a)] * 3, [(cx - 12, cy - 18), (cx - 12, cy + 18), (cx + 18, cy)])
        ui.text(s, "PyConsole", 54, (cx, cy + 110), ui.WHITE, bold=True, center=True, alpha=int(255 * p))
        ui.text(s, "press any button", 20, (cx, cy + 170), ui.GREY, center=True,
                alpha=int(120 + 120 * math.sin(self.t * 4)) if self.t > 1.5 else 0)

    def _draw_home(self, s):
        ui.gradient(s)
        ui.particles(s, self.t)
        ui.text(s, "Games", 26, (60, 40), ui.WHITE, bold=True)
        ui.text(s, "Media", 26, (170, 40), ui.GREY)
        ui.text(s, time.strftime("%H:%M"), 24, (ui.WIDTH - 110, 40), ui.WHITE)
        ui.trophy(s, (ui.WIDTH - 250, 56), 26)
        ui.text(s, f"{len(self.save.trophies)}/{len(TROPHY_NAMES)}", 22, (ui.WIDTH - 230, 42), ui.GOLD)

        base_x = 60 - self.scroll * (TILE_W * 0.55 + TILE_GAP)
        y = 130
        x = base_x
        for i, item in enumerate(self.items):
            focused = i == self.selected
            w, h = (TILE_W, TILE_H) if focused else (int(TILE_W * 0.55), int(TILE_H * 0.55))
            rect = pygame.Rect(int(x), y, w, h)
            if item == "trophies":
                ui.rounded(s, (60, 50, 20), rect)
                ui.trophy(s, rect.center, 90 if focused else 50)
            else:
                icon = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
                item(random.Random(0)).draw_icon(icon, icon.get_rect())
                s.blit(pygame.transform.smoothscale(icon, (w, h)), rect)
            if focused:
                ui.rounded(s, ui.WHITE, rect.inflate(10, 10), 22, 4)
            x += w + TILE_GAP

        item = self.items[self.selected]
        if item == "trophies":
            title, sub, extra = "Trophies", "Your achievements across every game", ""
        else:
            best = self.save.high_scores.get(item.key, 0)
            title, sub, extra = item.title, item.subtitle, f"Best score: {best}"
        ui.text(s, title, 52, (60, 380), ui.WHITE, bold=True)
        ui.text(s, sub, 24, (62, 450), ui.GREY)
        ui.text(s, extra, 22, (62, 490), ui.GOLD)
        play = pygame.Rect(60, 545, 200, 56)
        ui.rounded(s, ui.WHITE, play, 28)
        ui.text(s, "Open" if item == "trophies" else "Play", 26, play.center, (10, 20, 40), bold=True, center=True)
        ui.button_hint(s, [("← →", "Browse"), ("Enter", "Select")])

    def _draw_trophies(self, s):
        ui.gradient(s, (20, 16, 6), (60, 46, 12))
        ui.text(s, "Trophies", 48, (60, 50), ui.WHITE, bold=True)
        for i, (tid, desc) in enumerate(TROPHY_NAMES.items()):
            got = tid in self.save.trophies
            row = pygame.Rect(60, 140 + i * 90, ui.WIDTH - 120, 72)
            ui.rounded(s, (70, 58, 20) if got else (40, 36, 30), row, 14)
            ui.trophy(s, (row.x + 40, row.centery), 40, ui.GOLD if got else (90, 86, 80))
            ui.text(s, desc, 26, (row.x + 90, row.y + 20), ui.WHITE if got else ui.GREY)
        ui.button_hint(s, [("Esc", "Back")])

    def _draw_pause(self, s):
        shade = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        s.blit(shade, (0, 0))
        ui.text(s, "Paused", 48, (ui.WIDTH // 2, 250), ui.WHITE, bold=True, center=True)
        for i, label in enumerate(("Resume", "Quit to home")):
            rect = pygame.Rect(0, 0, 320, 56)
            rect.center = (ui.WIDTH // 2, 340 + i * 76)
            ui.rounded(s, ui.WHITE if i == self.pause_choice else (60, 70, 100), rect, 28)
            ui.text(s, label, 24, rect.center, (10, 20, 40) if i == self.pause_choice else ui.WHITE, bold=True, center=True)

    def _draw_game_over(self, s):
        shade = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 160))
        s.blit(shade, (0, 0))
        won = bool(self.game.earned & {"pong_win", "breakout_clear"})
        ui.text(s, "You win!" if won else "Game over", 56, (ui.WIDTH // 2, 290), ui.WHITE, bold=True, center=True)
        ui.text(s, f"Score {self.game.score}   Best {self.save.high_scores.get(self.game.key, 0)}", 28,
                (ui.WIDTH // 2, 370), ui.GOLD, center=True)
        ui.button_hint(s, [("Enter", "Back to home")])

    def _draw_toasts(self, s):
        for i, (msg, left) in enumerate(self.toasts):
            slide = min(1, (5 - left) * 4) if left > 4.75 else min(1, left * 3)
            img = ui.font(20, True).render(msg, True, ui.WHITE)
            rect = pygame.Rect(0, 0, img.get_width() + 70, 56)
            rect.topright = (ui.WIDTH - 24 + int((1 - slide) * (rect.width + 40)), 24 + i * 66)
            ui.rounded(s, (30, 34, 50), rect, 14)
            ui.trophy(s, (rect.x + 30, rect.centery), 28)
            s.blit(img, img.get_rect(midleft=(rect.x + 56, rect.centery)))


def _pad_actions(event, state):
    """Translate gamepad events into (action, pressed) pairs."""
    out = []
    if event.type == pygame.JOYBUTTONDOWN and event.button in PAD_BUTTONS:
        out.append((PAD_BUTTONS[event.button], True))
    elif event.type == pygame.JOYHATMOTION:
        x, y = event.value
        for action, active in (("left", x < 0), ("right", x > 0), ("up", y > 0), ("down", y < 0)):
            if active != (action in state):
                out.append((action, active))
    elif event.type == pygame.JOYAXISMOTION and event.axis in (0, 1):
        neg, pos = ("left", "right") if event.axis == 0 else ("up", "down")
        for action, active in ((neg, event.value < -0.5), (pos, event.value > 0.5)):
            if active != (action in state):
                out.append((action, active))
    for action, pressed in out:
        (state.add if pressed else state.discard)(action)
    return out


def main():
    pygame.init()
    pygame.display.set_caption("PyConsole")
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT), pygame.SCALED | pygame.RESIZABLE)
    pads = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    console = Console(screen)
    clock = pygame.time.Clock()
    pad_state = set()
    while console.running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                console.running = False
            elif event.type == pygame.KEYDOWN and event.key in KEYMAP:
                console.press(KEYMAP[event.key])
            elif event.type == pygame.KEYUP and event.key in KEYMAP:
                console.release(KEYMAP[event.key])
            elif event.type == pygame.JOYDEVICEADDED:
                pads.append(pygame.joystick.Joystick(event.device_index))
            else:
                for action, pressed in _pad_actions(event, pad_state):
                    (console.press if pressed else console.release)(action)
        console.update(dt)
        console.draw()
        pygame.display.flip()
    pygame.quit()
