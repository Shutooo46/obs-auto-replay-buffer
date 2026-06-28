import json
import time
import sys
import psutil
import obsws_python as obs


def load_config(path: str = "config.json") -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_running_exe_names() -> set[str]:
    names = set()
    for p in psutil.process_iter(["name"]):
        try:
            names.add(p.info["name"].lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return names


def is_replay_buffer_active(client: obs.ReqClient) -> bool:
    return client.get_replay_buffer_status().output_active


def start_replay_buffer(client: obs.ReqClient) -> None:
    if not is_replay_buffer_active(client):
        client.start_replay_buffer()


def stop_replay_buffer(client: obs.ReqClient) -> None:
    if is_replay_buffer_active(client):
        client.stop_replay_buffer()


def connect_to_obs(config: dict) -> obs.ReqClient:
    return obs.ReqClient(
        host=config["obs_host"],
        port=config["obs_port"],
        password=config["obs_password"],
    )


def main() -> None:
    config = load_config()
    enabled_games = [g for g in config["games"] if g.get("enabled", True)]
    poll_interval = config.get("poll_interval", 5)

    print("OBS に接続中...")
    try:
        client = connect_to_obs(config)
    except Exception as e:
        print(f"OBS への接続に失敗しました: {e}")
        print("OBS が起動していて WebSocket が有効になっているか確認してください。")
        sys.exit(1)

    print("接続成功。ゲームの監視を開始します。")
    print(f"監視対象: {[g['name'] for g in enabled_games]}")

    active_game = None

    while True:
        try:
            running = get_running_exe_names()

            if active_game is None:
                for game in enabled_games:
                    if game["exe"].lower() in running:
                        active_game = game
                        print(f"[検出] {game['name']} が起動しました → リプレイバッファ開始")
                        start_replay_buffer(client)
                        break
            else:
                if active_game["exe"].lower() not in running:
                    print(f"[終了] {active_game['name']} が終了しました → リプレイバッファ停止")
                    stop_replay_buffer(client)
                    active_game = None

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            print("OBS との接続を再試行します...")
            time.sleep(poll_interval)
            try:
                client = connect_to_obs(config)
                print("再接続成功。")
            except Exception:
                print("再接続に失敗しました。次のサイクルで再試行します。")

        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
