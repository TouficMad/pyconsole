"""Built-in games. Each game reacts to abstract actions (up, down, left, right,
confirm), so the console can drive it from a keyboard, a gamepad or a test."""
from .breakout import Breakout
from .pong import Pong
from .snake import Snake

GAMES = [Snake, Pong, Breakout]
