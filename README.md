# obs-auto-replay-buffer

ゲーム起動時に自動でOBSのリプレイバッファをONにするPythonスクリプトです。

## 概要

- OBS起動時ではなく、**指定したゲームの起動を検出したとき**にリプレイバッファを自動開始
- ゲーム終了時に自動停止（設定でオフにしてずっとオンのままにすることも可能）
- ゲームごとに有効/無効を設定可能
- OBS WebSocket API を使ってOBSを制御
- Windows起動時に自動常駐させることも可能

## 必要環境

- OBS Studio 28以降（WebSocket機能内蔵）
- Python 3.10以降

## セットアップ

### 1. ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. OBSのWebSocket設定

OBS → ツール → WebSocketサーバー設定 → 「WebSocketサーバーを有効にする」にチェック

### 3. config.jsonを編集

```json
{
  "obs_host": "localhost",
  "obs_port": 4455,
  "obs_password": "OBSのWebSocketパスワード",
  "poll_interval": 5,
  "stop_on_game_exit": true,
  "games": [
    { "name": "Apex Legends", "exe": "r5apex.exe", "enabled": true },
    { "name": "Valorant", "exe": "VALORANT-Win64-Shipping.exe", "enabled": true }
  ]
}
```

| 設定項目 | 説明 |
|----------|------|
| `obs_host` | OBSが動いているPC（基本そのまま） |
| `obs_port` | WebSocketのポート番号（デフォルト: 4455） |
| `obs_password` | OBSのWebSocketパスワード |
| `poll_interval` | ゲーム検出の間隔（秒）（デフォルト: 5） |
| `stop_on_game_exit` | ゲーム終了時にリプレイバッファを止めるか（`false`にするとずっとオン） |

## 使い方

### スクリプトを起動

```bash
python main.py
```

### ゲームのexe名がわからないとき

ゲームを起動した状態で以下を実行するとプロセス一覧が確認できます。

```bash
# 全プロセスを表示
python find_game.py

# キーワードで絞り込み
python find_game.py apex
```

表示されたexe名を `config.json` の `"exe"` にコピーしてください。

### Windows起動時に自動常駐させる

```bash
# 自動常駐をON
python setup_startup.py enable

# 自動常駐をOFF
python setup_startup.py disable

# 現在の状態を確認
python setup_startup.py status
```

## ライセンス

MIT
