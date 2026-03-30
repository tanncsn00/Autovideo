@echo off
title MoneyPrinterTurbo Desktop

echo === Setting up environment ===
set PATH=%USERPROFILE%\.cargo\bin;%PATH%

REM Load MSVC environment
for /f "usebackq tokens=*" %%i in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath`) do set VSINSTALLDIR=%%i
if exist "%VSINSTALLDIR%\VC\Auxiliary\Build\vcvars64.bat" (
    call "%VSINSTALLDIR%\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
    echo MSVC environment loaded
) else (
    echo WARNING: MSVC not found, build may fail
)

echo === Killing old processes ===
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":18080.*LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":1420.*LISTENING"') do taskkill /PID %%a /F >nul 2>&1

echo === Starting Python sidecar ===
cd /d E:\tvk\MoneyPrinterTurbo-v2
start /B python main.py --port 18080 --mode desktop

echo Waiting for sidecar...
:wait
timeout /t 2 /nobreak >nul
curl -s http://127.0.0.1:18080/api/v1/ping >nul 2>&1
if errorlevel 1 goto wait
echo Sidecar ready!

echo === Starting Tauri Desktop App ===
cd /d E:\tvk\MoneyPrinterTurbo-v2\desktop
npx tauri dev

pause
