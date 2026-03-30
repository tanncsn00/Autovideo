@echo off
echo === MoneyPrinterTurbo Desktop (dev mode) ===

cd /d "%~dp0\.."

echo Starting Python sidecar on port 18080...
start /B python main.py --port 18080 --mode desktop

echo Waiting for sidecar...
:wait_loop
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:18080/api/v1/ping >nul 2>&1
if errorlevel 1 goto wait_loop
echo Sidecar ready!

if exist "desktop" (
    echo Starting Tauri dev...
    cd desktop
    call npm run tauri dev
) else (
    echo desktop/ directory not found. Running sidecar only.
    echo Press Ctrl+C to stop.
    pause
)

taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main.py*" 2>nul
echo Dev environment stopped.
