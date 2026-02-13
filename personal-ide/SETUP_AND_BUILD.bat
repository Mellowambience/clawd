@echo off
REM MIST Visual Interface - Setup and Build Script for Windows
REM This script sets up the environment and builds the application

echo ========================================
echo MIST Visual Interface - Setup and Build
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Python is installed
echo.

REM Check if we're in the right directory
if not exist "LAUNCH_VISUAL.py" (
    echo ERROR: LAUNCH_VISUAL.py not found
    echo Please run this script from the personal-ide directory
    pause
    exit /b 1
)

echo Checking for virtual environment...
if exist "mist_env" (
    echo Virtual environment already exists
) else (
    echo Creating virtual environment...
    python -m venv mist_env
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
)

echo Activating virtual environment...
call mist_env\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Installing dependencies individually...
    pip install Pillow pygame aiohttp websockets
)

echo.
echo Testing application...
python -c "import LAUNCH_VISUAL; print('Application imports successfully!')"
if errorlevel 1 (
    echo WARNING: Application test failed, but continuing...
)

echo.
echo Available commands:
echo   build-app      - Build the application executable
echo   run            - Run the application directly
echo   build-source   - Create source distribution only
echo.
set /p command="Enter command (build-app/run/build-source): "

if "%command%"=="build-app" (
    echo Building application with PyInstaller...
    pip install pyinstaller
    pyinstaller --onefile --windowed --name "MIST_Visual_Interface" --add-data "sprites;sprites" LAUNCH_VISUAL.py
    echo.
    echo Build complete! Check the dist folder for the executable.
) else if "%command%"=="run" (
    echo Starting MIST Visual Interface...
    echo Press Ctrl+C to stop
    python LAUNCH_VISUAL.py
) else if "%command%"=="build-source" (
    echo Creating source distribution...
    python build-app.py
) else (
    echo Invalid command: %command%
)

echo.
echo Setup and build script completed.
pause