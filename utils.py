import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_CONFIG: dict = {
    "obs_host": "localhost",
    "obs_port": 4455,
    "obs_password": "",
    "poll_interval": 5,
    "stop_on_game_exit": True,
    "games": [],
    "ignored": [],
    "priority_order": [],
}
