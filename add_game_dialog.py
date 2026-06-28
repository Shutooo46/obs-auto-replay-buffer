import json
import tkinter as tk
from tkinter import ttk

from utils import CONFIG_PATH


def show_add_game_dialog(exe_name: str) -> None:
    root = tk.Tk()
    root.title("新しいゲームを検出しました")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    result: dict = {"action": None, "name": None}

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="新しいアプリを検出しました", font=("", 11, "bold")).pack()
    ttk.Label(frame, text=exe_name, foreground="gray").pack(pady=(2, 12))

    ttk.Label(frame, text="ゲーム名:").pack(anchor="w")
    name_var = tk.StringVar(value=exe_name.replace(".exe", "").replace(".EXE", ""))
    entry = ttk.Entry(frame, textvariable=name_var, width=28)
    entry.pack(fill="x", pady=(2, 12))
    entry.focus()

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x")

    def add() -> None:
        result["action"] = "add"
        result["name"] = name_var.get().strip()
        root.destroy()

    def ignore() -> None:
        result["action"] = "ignore"
        root.destroy()

    ttk.Button(btn_frame, text="追加する", command=add, padding=(12, 4)).pack(side="left", padx=(0, 6))
    ttk.Button(btn_frame, text="今後無視する", command=ignore).pack(side="left")

    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) // 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) // 2
    root.geometry(f"+{x}+{y}")

    root.mainloop()

    if result["action"] == "add" and result["name"]:
        _save_game(exe_name, result["name"])
    elif result["action"] == "ignore":
        _save_ignored(exe_name)


def _save_game(exe_name: str, game_name: str) -> None:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    config["games"].append({"name": game_name, "exe": exe_name, "enabled": True})
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def _save_ignored(exe_name: str) -> None:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    ignored = config.get("ignored", [])
    if exe_name not in ignored:
        ignored.append(exe_name)
    config["ignored"] = ignored
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
