@echo off
echo ==============================
echo  OBS Auto Replay Buffer
echo  ビルドスクリプト
echo ==============================
echo.

echo [1/2] PyInstallerをインストール中...
pip install pyinstaller >nul 2>&1

echo [2/2] exeをビルド中...
pyinstaller --noconsole ^
  --onedir ^
  --name "obs-auto-replay-buffer" ^
  --hidden-import "pystray._win32" ^
  tray_app.py

echo.
echo ==============================
echo  ビルド完了！
echo  dist\obs-auto-replay-buffer\
echo  フォルダを配布してください。
echo ==============================
pause
