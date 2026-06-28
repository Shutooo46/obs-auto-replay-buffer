import sys
import os
from pathlib import Path

STARTUP_FOLDER = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"))
BAT_NAME = "obs-auto-replay-buffer.bat"


def get_bat_path() -> Path:
    return STARTUP_FOLDER / BAT_NAME


def get_script_dir() -> Path:
    return Path(__file__).parent.resolve()


def enable() -> None:
    script_dir = get_script_dir()
    bat_content = (
        "@echo off\n"
        f'cd /d "{script_dir}"\n'
        "pythonw tray_app.py\n"
    )
    bat_path = get_bat_path()
    bat_path.write_text(bat_content, encoding="utf-8")
    print(f"自動常駐を有効にしました。")
    print(f"次回Windowsログイン時から自動で起動します: {bat_path}")


def disable() -> None:
    bat_path = get_bat_path()
    if bat_path.exists():
        bat_path.unlink()
        print("自動常駐を無効にしました。")
    else:
        print("自動常駐は既に無効です。")


def status() -> None:
    bat_path = get_bat_path()
    if bat_path.exists():
        print("自動常駐: 有効")
        print(f"登録先: {bat_path}")
    else:
        print("自動常駐: 無効")


def main() -> None:
    if len(sys.argv) < 2:
        print("使い方: python setup_startup.py [enable|disable|status]")
        print("  enable  - Windows起動時に自動で常駐を開始")
        print("  disable - 自動常駐を解除")
        print("  status  - 現在の状態を確認")
        sys.exit(1)

    command = sys.argv[1]
    if command == "enable":
        enable()
    elif command == "disable":
        disable()
    elif command == "status":
        status()
    else:
        print(f"不明なコマンド: {command}")
        print("使い方: python setup_startup.py [enable|disable|status]")
        sys.exit(1)


if __name__ == "__main__":
    main()
