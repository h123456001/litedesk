@echo off
REM LiteDesk Client Launcher for Windows
REM This script provides a user-friendly way to start the LiteDesk client

title LiteDesk Client Launcher
color 0B

echo ======================================
echo   LiteDesk Client Launcher
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
echo 1. May need to run as Administrator for some features
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

REM Start the client
echo ======================================
echo   Starting LiteDesk Client...
echo ======================================
echo.

python client.py

REM If client exits, show message
echo.
echo Client stopped.
pause
