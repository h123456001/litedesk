@echo off
REM LiteDesk Server Launcher for Windows
REM This script provides a user-friendly way to start the LiteDesk server

title LiteDesk Server Launcher
color 0A

echo ======================================
echo   LiteDesk Server Launcher
echo ======================================
echo.

echo Platform: Windows
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from python.org
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %PYTHON_VERSION%
echo.

REM Check if dependencies are installed
echo Checking dependencies...

python -c "import mss, PIL, pynput, PyQt5" >nul 2>&1
if errorlevel 1 (
    echo Some dependencies are missing
    echo Installing dependencies...
    pip install -r requirements.txt
    
    if errorlevel 1 (
        echo Failed to install dependencies
        echo.
        pause
        exit /b 1
    )
    echo.
) else (
    echo All dependencies are installed
    echo.
)

REM Platform-specific instructions
echo ======================================
echo   Platform-Specific Notes
echo ======================================
echo Windows Requirements:
echo 1. Windows Defender Firewall will prompt to allow
echo    the application. Select "Private networks" and
echo    click Allow.
echo 2. May need to run as Administrator for some features
echo.

echo Network Configuration:
echo - Server will listen on port 9876
echo - Make sure your firewall allows incoming connections
echo.

REM Check for admin rights
net session >nul 2>&1
if errorlevel 1 (
    echo Note: Not running as Administrator
    echo Some input control features may not work
    echo.
) else (
    echo Running as Administrator
    echo.
)

REM Start the server
echo ======================================
echo   Starting LiteDesk Server...
echo ======================================
echo.

python server.py

REM If server exits, show message
echo.
echo Server stopped.
pause
