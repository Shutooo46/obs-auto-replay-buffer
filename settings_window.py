import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from find_game import get_processes
from utils import CONFIG_PATH


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def _fetch_obs_games(config: dict) -> list[dict]:
    try:
        from main import connect_to_obs, get_obs_game_exes
        client = connect_to_obs(config)
        games = get_obs_game_exes(client)
        try:
            client.base_client.ws.close()
        except Exception:
            pass
        return games
    except Exception:
        return []


class ProcessPickerDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, on_select):
        super().__init__(parent)
        self.title("起動中のプロセスから選ぶ")
        self.resizable(False, False)
        self.grab_set()
        self.on_select = on_select

        self.all_processes = get_processes(None)

        ttk.Label(self, text="ゲームを起動した状態で選んでください", padding=(10, 8)).pack()

        search_frame = ttk.Frame(self, padding=(10, 0))
        search_frame.pack(fill="x")
        ttk.Label(search_frame, text="絞り込み:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        ttk.Entry(search_frame, textvariable=self.search_var, width=28).pack(side="left", padx=(5, 0))

        self.listbox = tk.Listbox(self, width=42, height=14, selectmode="single")
        self.listbox.pack(padx=10, pady=(5, 0))
        self.listbox.bind("<Double-Button-1>", lambda _: self._confirm())

        self._fill_list(self.all_processes)

        ttk.Button(self, text="選択", command=self._confirm, padding=(20, 4)).pack(pady=8)

    def _fill_list(self, names: list[str]) -> None:
        self.listbox.delete(0, "end")
        for name in names:
            self.listbox.insert("end", name)

    def _on_search(self, *_) -> None:
        keyword = self.search_var.get().lower()
        filtered = [n for n in self.all_processes if keyword in n.lower()]
        self._fill_list(filtered)

    def _confirm(self) -> None:
        sel = self.listbox.curselection()
        if sel:
            self.on_select(self.listbox.get(sel[0]))
        self.destroy()


class SettingsWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("ゲーム設定 - OBS Auto Replay Buffer")
        self.root.resizable(False, False)
        self.config = load_config()

        # OBSからゲーム一覧を取得
        self._obs_games = _fetch_obs_games(self.config)
        self._obs_connected = len(self._obs_games) > 0

        # 優先順位リスト: [{"exe": "...", "name": "..."}]
        self._priority_items: list[dict] = []
        self._build_priority_items()

        self._build_ui()
        self._refresh_list()
        self._refresh_priority_list()

    def _build_priority_items(self) -> None:
        known: dict[str, str] = {}
        for g in self._obs_games:
            known[g["exe"].lower()] = g["name"]
        for g in self.config.get("games", []):
            if g["exe"].lower() not in known:
                known[g["exe"].lower()] = g["name"]

        priority_order = self.config.get("priority_order", [])
        result: list[dict] = []
        remaining = dict(known)
        for exe in priority_order:
            if exe.lower() in remaining:
                result.append({"exe": exe.lower(), "name": remaining.pop(exe.lower())})
        for exe_lower, name in remaining.items():
            result.append({"exe": exe_lower, "name": name})

        self._priority_items = result

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        # ---- 手動登録セクション ----
        ttk.Label(frame, text="登録済みゲーム（手動）", font=("", 10, "bold")).pack(anchor="w")

        self.tree = ttk.Treeview(
            frame,
            columns=("name", "exe", "enabled"),
            show="headings",
            height=5,
            selectmode="browse",
        )
        self.tree.heading("name", text="ゲーム名")
        self.tree.heading("exe", text="exeファイル名")
        self.tree.heading("enabled", text="有効")
        self.tree.column("name", width=170)
        self.tree.column("exe", width=210)
        self.tree.column("enabled", width=50, anchor="center")
        self.tree.pack(fill="x", pady=(4, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(4, 0))
        ttk.Button(btn_frame, text="有効/無効を切り替え", command=self._toggle_enabled).pack(side="left", padx=(0, 4))
        ttk.Button(btn_frame, text="削除", command=self._delete_game).pack(side="left")

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(frame, text="ゲームを追加", font=("", 10, "bold")).pack(anchor="w", pady=(0, 4))

        add_frame = ttk.Frame(frame)
        add_frame.pack(fill="x")

        ttk.Label(add_frame, text="ゲーム名:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.name_var, width=26).grid(row=0, column=1, sticky="w")

        ttk.Label(add_frame, text="exe名:").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=(6, 0))
        self.exe_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.exe_var, width=26).grid(row=1, column=1, sticky="w", pady=(6, 0))
        ttk.Button(add_frame, text="起動中から選ぶ", command=self._open_picker).grid(
            row=1, column=2, padx=(6, 0), pady=(6, 0)
        )

        ttk.Button(frame, text="追加", command=self._add_game).pack(anchor="e", pady=(6, 0))

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=8)

        # ---- 優先順位セクション ----
        ttk.Label(frame, text="ゲームの優先順位", font=("", 10, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text="上にあるゲームが優先されます。複数のゲームが同時に起動している場合、上のゲームが有効になります。",
            foreground="gray",
            wraplength=440,
        ).pack(anchor="w", pady=(2, 4))

        if not self._obs_connected:
            ttk.Label(
                frame,
                text="※ OBSが起動していないため、OBS自動検出ゲームは表示されていません。",
                foreground="orange",
            ).pack(anchor="w", pady=(0, 4))

        priority_frame = ttk.Frame(frame)
        priority_frame.pack(fill="x")

        self.priority_listbox = tk.Listbox(
            priority_frame, height=6, selectmode="single", activestyle="none"
        )
        self.priority_listbox.pack(side="left", fill="x", expand=True)

        prio_btn = ttk.Frame(priority_frame)
        prio_btn.pack(side="left", padx=(8, 0))
        ttk.Button(prio_btn, text="↑ 上へ", command=self._priority_up, width=8).pack(pady=(0, 4))
        ttk.Button(prio_btn, text="↓ 下へ", command=self._priority_down, width=8).pack()

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Button(frame, text="保存して閉じる", command=self._save_and_close, padding=(16, 4)).pack(anchor="e")

    def _refresh_list(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for game in self.config["games"]:
            enabled = "✓" if game.get("enabled", True) else "✗"
            self.tree.insert("", "end", values=(game["name"], game["exe"], enabled))

    def _refresh_priority_list(self) -> None:
        self.priority_listbox.delete(0, "end")
        for item in self._priority_items:
            self.priority_listbox.insert("end", f"  {item['name']}  ({item['exe']})")

    def _selected_index(self) -> int | None:
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.index(sel[0])

    def _toggle_enabled(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        game = self.config["games"][idx]
        game["enabled"] = not game.get("enabled", True)
        self._refresh_list()

    def _delete_game(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        name = self.config["games"][idx]["name"]
        if messagebox.askyesno("確認", f'「{name}」を削除しますか？', parent=self.root):
            self.config["games"].pop(idx)
            self._build_priority_items()
            self._refresh_list()
            self._refresh_priority_list()

    def _open_picker(self) -> None:
        ProcessPickerDialog(self.root, on_select=lambda name: self.exe_var.set(name))

    def _add_game(self) -> None:
        name = self.name_var.get().strip()
        exe = self.exe_var.get().strip()
        if not name or not exe:
            messagebox.showwarning("入力エラー", "ゲーム名とexe名を両方入力してください。", parent=self.root)
            return
        self.config["games"].append({"name": name, "exe": exe, "enabled": True})
        self.name_var.set("")
        self.exe_var.set("")
        self._build_priority_items()
        self._refresh_list()
        self._refresh_priority_list()

    def _priority_up(self) -> None:
        sel = self.priority_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx == 0:
            return
        items = self._priority_items
        items[idx - 1], items[idx] = items[idx], items[idx - 1]
        self._refresh_priority_list()
        self.priority_listbox.selection_set(idx - 1)

    def _priority_down(self) -> None:
        sel = self.priority_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._priority_items) - 1:
            return
        items = self._priority_items
        items[idx], items[idx + 1] = items[idx + 1], items[idx]
        self._refresh_priority_list()
        self.priority_listbox.selection_set(idx + 1)

    def _save_and_close(self) -> None:
        self.config["priority_order"] = [item["exe"] for item in self._priority_items]
        save_config(self.config)
        messagebox.showinfo("保存完了", "設定を保存しました。\n反映するには監視を再起動してください。", parent=self.root)
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def open_settings() -> None:
    SettingsWindow().run()


def open_settings_async() -> None:
    threading.Thread(target=open_settings, daemon=True).start()
