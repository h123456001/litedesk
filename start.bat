@echo off
REM LiteDesk Quick Start Script for Windows

echo ===========================================
echo   LiteDesk - Simple P2P Remote Desktop
echo ===========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from python.org
    pause
    exit /b 1
)

echo Select mode:
echo 1) Start Server (share your desktop)
echo 2) Start Client (connect to remote desktop)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Starting LiteDesk Server...
    echo After starting, share your IP address with the client.
    echo.
    python server.py
) else if "%choice%"=="2" (
    echo.
    echo Starting LiteDesk Client...
    echo You will need the server's IP address to connect.
    echo.
    python client.py
) else (
    echo Invalid choice
    pause
    exit /b 1
)
