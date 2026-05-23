$ErrorActionPreference = "Stop"

python -m pip install -r requirements.txt pyinstaller
npm ci
npm run build:win:monitor

New-Item -ItemType Directory -Force -Path "dist-monitor/win" | Out-Null
Copy-Item "dist/auction-monitor.exe" "dist-monitor/win/auction-monitor.exe" -Force

npm run build:win
