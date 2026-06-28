import subprocess
import sys
import threading
import time
from pathlib import Path

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as Item

from main import (
    connect_to_obs,
    get_running_exe_names,
    load_config,
    start_replay_buffer,
    stop_replay_buffer,
)
from setup_startup import disable as startup_disable
from setup_startup import enable as startup_enable
from setup_startup import get_bat_path
from settings_window import open_settings_async

CONFIG_PATH = Path(__file__).parent / "config.json"

monitoring = False
obs_client = None
config: dict = {}
active_game = None
_icon_ref: pystray.Icon | None = None


def make_icon(active: bool) -> Image.Image:
    color = (0, 184, 148) if active else (99, 110, 114)
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([4, 4, 60, 60], fill=color)
    return img


def update_icon() -> None:
    if _icon_ref is None:
        return
    _icon_ref.icon = make_icon(monitoring)
    _icon_ref.title = f"OBS Auto Replay Buffer - {'監視中' if monitoring else '停止中'}"


def monitor_loop() -> None:
    global active_game, obs_client, monitoring

    while monitoring:
        try:
            if obs_client is None:
                obs_client = connect_to_obs(config)

            running = get_running_exe_names()
            enabled_games = [g for g in config["games"] if g.get("enabled", True)]
            stop_on_exit = config.get("stop_on_game_exit", True)

            if active_game is None:
                for game in enabled_games:
                    if game["exe"].lower() in running:
                        active_game = game
                        start_replay_buffer(obs_client)
                        if _icon_ref:
                            _icon_ref.notify(
                                f"{game['name']} を検出しました",
                                "リプレイバッファ開始",
                            )
                        break
            else:
                if active_game["exe"].lower() not in running:
                    if stop_on_exit:
                        stop_replay_buffer(obs_client)
                        if _icon_ref:
                            _icon_ref.notify(
                                f"{active_game['name']} が終了しました",
                                "リプレイバッファ停止",
                            )
                    active_game = None

        except Exception:
            obs_client = None

        time.sleep(config.get("poll_interval", 5))


def start_monitoring(icon=None, item=None) -> None:
    global monitoring, obs_client, config
    if monitoring:
        return
    config = load_config(str(CONFIG_PATH))
    obs_client = None
    monitoring = True
    threading.Thread(target=monitor_loop, daemon=True).start()
    update_icon()


def stop_monitoring(icon=None, item=None) -> None:
    global monitoring, active_game, obs_client
    monitoring = False
    active_game = None
    obs_client = None
    update_icon()


def toggle_startup(icon, item) -> None:
    if get_bat_path().exists():
        startup_disable()
    else:
        startup_enable()


def is_startup_enabled(item) -> bool:
    return get_bat_path().exists()


def open_config(icon, item) -> None:
    subprocess.Popen(["notepad.exe", str(CONFIG_PATH)])


def on_quit(icon, item) -> None:
    global monitoring
    monitoring = False
    icon.stop()


def main() -> None:
    global _icon_ref, config
    config = load_config(str(CONFIG_PATH))

    icon = pystray.Icon(
        "obs-auto-replay-buffer",
        icon=make_icon(False),
        title="OBS Auto Replay Buffer - 停止中",
        menu=pystray.Menu(
            Item("監視を開始", start_monitoring, enabled=lambda item: not monitoring),
            Item("監視を停止", stop_monitoring, enabled=lambda item: monitoring),
            pystray.Menu.SEPARATOR,
            Item("ゲーム設定", open_settings_async),
            pystray.Menu.SEPARATOR,
            Item("Windows起動時に自動起動", toggle_startup, checked=is_startup_enabled),
            pystray.Menu.SEPARATOR,
            Item("終了", on_quit),
        ),
    )
    _icon_ref = icon
    start_monitoring()
    icon.run()


if __name__ == "__main__":
    main()
