import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from pyconsole import ui  # noqa: E402
from pyconsole.app import PLATINUM, Console  # noqa: E402
from pyconsole.games import Breakout, Pong, Snake  # noqa: E402
from pyconsole.storage import SaveData  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def display():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def console(tmp_path):
    surface = pygame.Surface((ui.WIDTH, ui.HEIGHT))
    return Console(surface, SaveData(tmp_path / "save.json"), random.Random(1))


def run(console, seconds, dt=1 / 60):
    for _ in range(int(seconds / dt)):
        console.update(dt)
        console.draw()


def test_boot_then_home(console):
    run(console, 1)
    assert console.state == "boot"
    console.press("confirm")
    assert console.state == "home"


def test_home_navigation_is_clamped(console):
    console.press("confirm")
    for _ in range(10):
        console.press("right")
    assert console.selected == len(console.items) - 1
    for _ in range(10):
        console.press("left")
    assert console.selected == 0


@pytest.mark.parametrize("index", [0, 1, 2])
def test_every_game_runs_until_game_over(console, index):
    console.press("confirm")
    for _ in range(index):
        console.press("right")
    console.press("confirm")
    assert console.state == "game"
    run(console, 300, dt=1 / 30)           # nobody plays: the game must end on its own
    assert console.game.over
    console.press("confirm")
    assert console.state == "home"


def test_pause_and_quit(console):
    console.press("confirm")
    console.press("confirm")                # start Snake
    run(console, 0.2)
    console.press("back")                   # pause
    assert console.paused
    snapshot = list(console.game.body)
    run(console, 1)
    assert console.game.body == snapshot    # frozen while paused
    console.press("down")
    console.press("confirm")                # quit to home
    assert console.state == "home"


def test_snake_trophy_and_high_score(console):
    console.press("confirm")
    console.press("confirm")
    game = console.game
    for _ in range(10):                     # feed the snake directly in front of its head
        head = game.body[0]
        game.food = (head[0] + game.direction[0], head[1] + game.direction[1])
        game.timer = game.step
        console.update(0)
    assert game.score == 10
    assert "snake_10" in console.save.trophies
    assert console.toasts


def test_platinum_after_all_trophies(console):
    console.save.trophies |= {"snake_10", "pong_win"}
    console.press("confirm")
    console.press("right")
    console.press("right")
    console.press("confirm")                # Brick Breaker
    console.game.bricks = console.game.bricks[:1]
    console.game.ball.update(console.game.bricks[0].center)
    console.update(1 / 60)
    assert {"breakout_clear", PLATINUM} <= console.save.trophies


def test_pong_player_wins_when_cpu_misses():
    game = Pong(random.Random(0))
    game.score = 6
    game.ball.update(ui.WIDTH + 10, 300)
    game.update(1 / 60)
    assert game.over and "pong_win" in game.earned


def test_snake_cannot_reverse_into_itself():
    game = Snake(random.Random(0))
    game.press("left")                      # moving right: reversing is ignored
    assert game.next_direction == (1, 0)


def test_breakout_loses_a_life():
    game = Breakout(random.Random(0))
    game.ball.update(100, ui.HEIGHT + 20)
    game.update(1 / 60)
    assert game.lives == 2 and not game.over


def test_save_data_roundtrip(tmp_path):
    path = tmp_path / "save.json"
    save = SaveData(path)
    assert save.record_score("snake", 5)
    assert not save.record_score("snake", 3)
    assert save.unlock("pong_win") and not save.unlock("pong_win")
    again = SaveData(path)
    assert again.high_scores == {"snake": 5} and again.trophies == {"pong_win"}


def test_corrupt_save_file_is_ignored(tmp_path):
    path = tmp_path / "save.json"
    path.write_text("{not json")
    assert SaveData(path).high_scores == {}
