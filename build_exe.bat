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

set "PYI_FAKE_MODULES=.venv\Lib\site-packages\PyInstaller\fake-modules"

if not exist "%PYI_FAKE_MODULES%" (
    echo ERROR: PyInstaller fake-modules folder not found.
    pause
    exit /b 1
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
    --paths "%PYI_FAKE_MODULES%" ^
    --hidden-import "_pyi_rth_utils" ^
    --hidden-import "_pyi_rth_utils.qt" ^
    --collect-all "PySide6" ^
    --collect-all "shiboken6" ^
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
