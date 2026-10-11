"""Theme, fonts and drawing helpers shared by the console screens and games."""
import math

import pygame

WIDTH, HEIGHT = 1280, 720
BG_TOP = (6, 12, 34)
BG_BOTTOM = (18, 40, 92)
ACCENT = (0, 112, 209)
WHITE = (245, 247, 252)
GREY = (150, 160, 185)
GOLD = (240, 196, 64)

_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("dejavusans,arial,helvetica", size, bold=bold)
    return _fonts[key]


def text(surface, msg, size, pos, color=WHITE, bold=False, center=False, alpha=255):
    img = font(size, bold).render(str(msg), True, color)
    if alpha < 255:
        img.set_alpha(alpha)
    rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
    surface.blit(img, rect)
    return rect


def gradient(surface, top=BG_TOP, bottom=BG_BOTTOM):
    h = surface.get_height()
    for y in range(0, h, 4):
        t = y / h
        color = [int(a + (b - a) * t) for a, b in zip(top, bottom)]
        pygame.draw.rect(surface, color, (0, y, surface.get_width(), 4))


def particles(surface, t, count=40):
    """Slowly drifting light particles, like a console home screen."""
    w, h = surface.get_size()
    for i in range(count):
        x = (i * 97 + t * (8 + i % 5) * 6) % w
        y = (i * 53 + math.sin(t * 0.5 + i) * 30) % h
        r = 1 + i % 3
        pygame.draw.circle(surface, (90, 140, 230), (int(x), int(y)), r)


def rounded(surface, color, rect, radius=18, width=0):
    pygame.draw.rect(surface, color, rect, width, border_radius=radius)


def button_hint(surface, hints, y=HEIGHT - 40):
    """Draw hints like ('Enter', 'Play') at the bottom right."""
    x = WIDTH - 40
    for key, label in reversed(hints):
        lab = font(18).render(label, True, GREY)
        x -= lab.get_width()
        surface.blit(lab, (x, y))
        k = font(16, True).render(key, True, WHITE)
        box = pygame.Rect(0, 0, k.get_width() + 16, 26)
        x -= box.width + 8
        box.topleft = (x, y - 3)
        rounded(surface, (60, 70, 100), box, 6)
        surface.blit(k, k.get_rect(center=box.center))
        x -= 28


def trophy(surface, center, size, color=GOLD):
    """A small trophy cup drawn with shapes (no emoji font needed)."""
    x, y = center
    s = size / 2
    pygame.draw.polygon(surface, color, [(x - s * 0.7, y - s * 0.8), (x + s * 0.7, y - s * 0.8),
                                         (x + s * 0.45, y + s * 0.1), (x - s * 0.45, y + s * 0.1)])
    pygame.draw.circle(surface, color, (x - s * 0.7, y - s * 0.45), s * 0.32, max(2, int(s * 0.12)))
    pygame.draw.circle(surface, color, (x + s * 0.7, y - s * 0.45), s * 0.32, max(2, int(s * 0.12)))
    pygame.draw.rect(surface, color, (x - s * 0.12, y + s * 0.1, s * 0.24, s * 0.45))
    pygame.draw.rect(surface, color, (x - s * 0.5, y + s * 0.55, s, s * 0.25), border_radius=3)
