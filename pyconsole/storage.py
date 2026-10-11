"""Save data: high scores and trophies, stored as JSON in the user's home folder."""
import json
import os
from pathlib import Path

DEFAULT_PATH = Path(os.getenv("PYCONSOLE_SAVE", Path.home() / ".pyconsole" / "save.json"))


class SaveData:
    def __init__(self, path=DEFAULT_PATH):
        self.path = Path(path)
        self.high_scores = {}
        self.trophies = set()
        self.load()

    def load(self):
        try:
            data = json.loads(self.path.read_text())
        except (OSError, ValueError):
            return
        self.high_scores = {k: int(v) for k, v in data.get("high_scores", {}).items()}
        self.trophies = set(data.get("trophies", []))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"high_scores": self.high_scores, "trophies": sorted(self.trophies)}
        self.path.write_text(json.dumps(data, indent=2))

    def record_score(self, game, score) -> bool:
        """Store a score. Returns True if it is a new high score."""
        if score > self.high_scores.get(game, 0):
            self.high_scores[game] = score
            self.save()
            return True
        return False

    def unlock(self, trophy) -> bool:
        """Unlock a trophy. Returns True the first time."""
        if trophy in self.trophies:
            return False
        self.trophies.add(trophy)
        self.save()
        return True
