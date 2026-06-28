import json
import tkinter as tk
from tkinter import ttk

from utils import CONFIG_PATH, DEFAULT_CONFIG


class SetupWizard:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("OBS Auto Replay Buffer - 初回設定")
        self.root.resizable(False, False)
        self.completed = False
        self._build_ui()
        self._center()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="OBS Auto Replay Buffer", font=("", 14, "bold")).pack()
        ttk.Label(frame, text="OBSのWebSocket設定を入力してください", padding=(0, 6)).pack()

        box = ttk.LabelFrame(frame, text="OBS WebSocket設定", padding=12)
        box.pack(fill="x", pady=8)

        def row(parent, label, var, show=""):
            f = ttk.Frame(parent)
            f.pack(fill="x", pady=3)
            ttk.Label(f, text=label, width=14, anchor="w").pack(side="left")
            e = ttk.Entry(f, textvariable=var, show=show, width=22)
            e.pack(side="left")
            return e

        self.host_var = tk.StringVar(value="localhost")
        self.port_var = tk.StringVar(value="4455")
        self.pw_var = tk.StringVar()

        row(box, "ホスト:", self.host_var)
        row(box, "ポート:", self.port_var)
        self.pw_entry = row(box, "パスワード:", self.pw_var, show="*")

        pw_row = ttk.Frame(box)
        pw_row.pack(fill="x")
        ttk.Button(pw_row, text="パスワードを表示/非表示", command=self._toggle_pw).pack(anchor="e")

        ttk.Button(frame, text="OBSへの接続をテスト", command=self._test_connection).pack(pady=(10, 2))

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(frame, textvariable=self.status_var)
        self.status_label.pack()

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Button(
            frame,
            text="設定を保存して始める →",
            command=self._save,
            padding=(20, 6),
        ).pack(anchor="e")

        ttk.Label(
            frame,
            text="OBS → ツール → WebSocketサーバー設定 から有効にできます",
            foreground="gray",
            wraplength=320,
            justify="center",
        ).pack(pady=(10, 0))

    def _toggle_pw(self) -> None:
        self.pw_entry.config(show="" if self.pw_entry.cget("show") == "*" else "*")

    def _test_connection(self) -> None:
        import obsws_python as obs

        self.status_var.set("接続中...")
        self.status_label.config(foreground="black")
        self.root.update()
        try:
            obs.ReqClient(
                host=self.host_var.get().strip(),
                port=int(self.port_var.get()),
                password=self.pw_var.get(),
                timeout=3,
            )
            self.status_var.set("✓ 接続成功！")
            self.status_label.config(foreground="green")
        except Exception:
            self.status_var.set("✗ 接続失敗。OBSが起動していてWebSocketが有効か確認してください。")
            self.status_label.config(foreground="red")

    def _save(self) -> None:
        config = dict(DEFAULT_CONFIG)
        config["obs_host"] = self.host_var.get().strip()
        config["obs_port"] = int(self.port_var.get().strip())
        config["obs_password"] = self.pw_var.get()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self.completed = True
        self.root.destroy()

    def _center(self) -> None:
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"+{x}+{y}")

    def run(self) -> bool:
        self.root.mainloop()
        return self.completed
