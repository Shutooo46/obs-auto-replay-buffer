import threading
import time

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as Item

from main import (
    connect_to_obs,
    get_obs_game_exes,
    get_running_exe_names,
    load_config,
    start_replay_buffer,
    stop_replay_buffer,
)
from setup_startup import disable as startup_disable
from setup_startup import enable as startup_enable
from setup_startup import get_bat_path
from settings_window import open_settings_async
from utils import CONFIG_PATH

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


def _activate_game(game: dict) -> None:
    global active_game
    active_game = game
    if "scene" in game:
        try:
            obs_client.set_current_program_scene(game["scene"])
        except Exception:
            pass
    start_replay_buffer(obs_client)
    if _icon_ref:
        scene_info = f" → シーン「{game['scene']}」に切替" if "scene" in game else ""
        _icon_ref.notify(
            f"{game['name']} を検出しました{scene_info}",
            "リプレイバッファ開始",
        )


def monitor_loop() -> None:
    global active_game, obs_client, monitoring

    while monitoring:
        try:
            if obs_client is None:
                obs_client = connect_to_obs(config)

            running = get_running_exe_names()

            # OBSのゲームキャプチャソースから取得（特定ウィンドウモード）
            obs_games = get_obs_game_exes(obs_client)

            # config.jsonの手動リスト
            manual_games = [g for g in config.get("games", []) if g.get("enabled", True)]

            # 両方を合わせてexeをキーにしたdict（手動リストが優先）
            all_games: dict[str, dict] = {g["exe"].lower(): g for g in manual_games}
            for g in obs_games:
                if g["exe"].lower() not in all_games:
                    all_games[g["exe"].lower()] = g

            # 優先順位リスト（indexが小さいほど優先度高）
            priority_order = [exe.lower() for exe in config.get("priority_order", [])]

            def get_priority(exe_lower: str) -> int:
                try:
                    return priority_order.index(exe_lower)
                except ValueError:
                    return len(priority_order)

            stop_on_exit = config.get("stop_on_game_exit", True)

            if active_game is None:
                # 優先度順に並べて最初に見つかったゲームを起動
                sorted_games = sorted(all_games.items(), key=lambda x: get_priority(x[0]))
                for exe_lower, game in sorted_games:
                    if exe_lower in running:
                        _activate_game(game)
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
                else:
                    # アクティブゲームより高優先度のゲームが起動したら切り替え
                    active_priority = get_priority(active_game["exe"].lower())
                    for exe_lower, game in all_games.items():
                        if exe_lower in running and exe_lower != active_game["exe"].lower():
                            if get_priority(exe_lower) < active_priority:
                                _activate_game(game)
                                break

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


def on_quit(icon, item) -> None:
    global monitoring
    monitoring = False
    icon.stop()


def needs_setup() -> bool:
    if not CONFIG_PATH.exists():
        return True
    try:
        cfg = load_config(str(CONFIG_PATH))
        return not cfg.get("obs_password")
    except Exception:
        return True


def main() -> None:
    global _icon_ref, config

    if needs_setup():
        from setup_wizard import SetupWizard
        completed = SetupWizard().run()
        if not completed:
            return

    config = load_config(str(CONFIG_PATH))

    icon = pystray.Icon(
        "obs-auto-replay-buffer",
        icon=make_icon(False),
        title="OBS Auto Replay Buffer - 停止中",
        menu=pystray.Menu(
            Item("監視を開始", start_monitoring, enabled=lambda item: not monitoring),
            Item("監視を停止", stop_monitoring, enabled=lambda item: monitoring),
            pystray.Menu.SEPARATOR,
            Item("ゲーム設定（手動登録）", open_settings_async),
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
