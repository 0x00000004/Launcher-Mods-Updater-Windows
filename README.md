Launcher Mods Updater [PC VERSION]

Desktop-приложение на Python + PySide6 для обновления модов Minecraft.

Возможности

- Загружает manifest с GitHub
- Проверяет папку %APPDATA%\.minecraft\mods
- Удаляет лишние .jar, которых нет в manifest
- Скачивает недостающие моды
- Показывает прогресс, список модов и лог
- Поддерживает сборку в .exe через PyInstaller

Структура

- main.py — точка входа
- ui.py — интерфейс
- downloader.py — загрузка manifest и модов
- build_exe.bat — сборка .exe с иконкой
- icon.ico — иконка приложения

Установка зависимостей

powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Запуск

powershell
.\.venv\Scripts\python.exe main.py

Manifest

PC-версия использует:
https://raw.githubusercontent.com/0x00000004/mod-updater-data/main/manifest-pc.json

