# obs-auto-replay-buffer

ゲーム起動時に自動でOBSのリプレイバッファをONにするツールです。

## 概要

- OBS起動時ではなく、**指定したゲームの起動を検出したとき**にリプレイバッファを自動開始
- ゲーム終了時に自動停止（設定でオフにしてずっとオンのままにすることも可能）
- GUIでゲームを簡単に追加・管理可能
- タスクバーのトレイに常駐して動作、ターミナル不要
- OBS WebSocket API を使ってOBSを制御

## 必要環境

- OBS Studio 28以降（WebSocket機能内蔵）
- Python 3.10以降

## セットアップ（初回のみ）

### 1. ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. OBSのWebSocket設定

OBS → ツール → WebSocketサーバー設定 → 「WebSocketサーバーを有効にする」にチェック

### 3. config.jsonのパスワードを設定

`config.json` を開いて `obs_password` をOBSのWebSocketパスワードに変更してください。

```json
{
  "obs_host": "localhost",
  "obs_port": 4455,
  "obs_password": "OBSのWebSocketパスワード",
  "poll_interval": 5,
  "stop_on_game_exit": true,
  "games": []
}
```

| 設定項目 | 説明 |
|----------|------|
| `obs_password` | OBSのWebSocketパスワード |
| `poll_interval` | ゲーム検出の間隔（秒）（デフォルト: 5） |
| `stop_on_game_exit` | ゲーム終了時にリプレイバッファを止めるか（`false` にするとずっとオン） |

## 使い方

### 起動

`start.bat` をダブルクリックするとタスクバーのトレイに常駐します。
起動と同時にゲームの監視が始まります。

### トレイアイコンの右クリックメニュー

| メニュー | 説明 |
|----------|------|
| 監視を開始 / 停止 | ゲーム監視のオン・オフ |
| ゲーム設定 | ゲームの追加・削除・有効無効の管理 |
| Windows起動時に自動起動 | PC起動時に自動で常駐させる（チェックで切り替え） |
| 終了 | アプリを終了 |

### ゲームの追加方法

1. ゲームを起動する
2. トレイアイコンを右クリック → **「ゲーム設定」**
3. 「起動中から選ぶ」ボタンでゲームのexeを選択
4. ゲーム名を入力して「追加」
5. 「保存して閉じる」→ 監視を再起動

## ライセンス

MIT
