@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo Building Launcher Mods Updater...
echo ==========================================

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found: .venv\Scripts\python.exe
    pause
    exit /b 1
)

if not exist "icon.ico" (
    echo ERROR: icon.ico not found in project folder.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\pyinstaller.exe" (
    echo PyInstaller not found. Installing...
    ".venv\Scripts\python.exe" -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Launcher Mods Updater.spec" del /f /q "Launcher Mods Updater.spec"

".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --onefile ^
    --name "Launcher Mods Updater" ^
    --icon "icon.ico" ^
    --add-data "icon.ico;." ^
    "main.py"

if errorlevel 1 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo Build complete:
echo %cd%\dist\Launcher Mods Updater.exe
pause
