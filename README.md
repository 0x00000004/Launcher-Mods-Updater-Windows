# Launcher Mods Updater [PC VERSION]

Desktop-приложение на Python + PySide6 для обновления модов Minecraft.

## Возможности

- Загружает manifest с GitHub
- Проверяет папку `%APPDATA%\.minecraft\mods`
- Удаляет лишние `.jar`, которых нет в manifest
- Скачивает недостающие моды
- Показывает прогресс, список модов и лог
- Поддерживает сборку в `.exe` через `PyInstaller`

## Структура

- `main.py` — точка входа
- `ui.py` — интерфейс
- `downloader.py` — загрузка manifest и модов
- `build_exe.bat` — сборка `.exe` с иконкой
- `icon.ico` — иконка приложения
- `requirements.txt` — файл содержащий зависимости

## Установка зависимостей

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Запуск

```powershell
.\.venv\Scripts\python.exe main.py
```

## Сборка `.exe`

```powershell
build_exe.bat
```

Готовый файл появится в папке:

```text
dist\Launcher Mods Updater.exe
```

## Manifest

PC-версия использует:

```text
https://raw.githubusercontent.com/0x00000004/mod-updater-data/main/manifest-pc.json
```
