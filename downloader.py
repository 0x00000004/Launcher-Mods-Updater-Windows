from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from PySide6.QtCore import QObject, Signal, Slot


MANIFEST_URL = (
    "https://raw.githubusercontent.com/0x00000004/mod-updater-data/main/manifest-pc.json"
)
BASE_DOWNLOAD_URL = "https://raw.githubusercontent.com/0x00000004/mod-updater-data/main/"
CHUNK_SIZE = 64 * 1024


@dataclass(slots=True)
class ModEntry:
    name: str
    file: str


class ModDownloaderWorker(QObject):
    started = Signal()
    finished = Signal(bool)
    manifest_loaded = Signal(str, list)
    mod_status_changed = Signal(int, str)
    log_message = Signal(str)
    progress_changed = Signal(int)
    error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._cancelled = False

    @Slot()
    def run(self) -> None:
        self.started.emit()
        self.progress_changed.emit(0)
        self.log_message.emit("Проверка обновлений...")

        try:
            manifest_data = self._download_json(MANIFEST_URL)
            version, mods = self._parse_manifest(manifest_data)
            self.manifest_loaded.emit(
                version, [{"name": entry.name, "file": entry.file} for entry in mods]
            )

            mods_dir = self._get_mods_dir()
            mods_dir.mkdir(parents=True, exist_ok=True)
            self.log_message.emit(f"Папка модов: {mods_dir}")
            self._remove_extra_mods(mods, mods_dir)

            missing = self._inspect_mods(mods, mods_dir)
            if not missing:
                self.progress_changed.emit(100)
                self.log_message.emit("Все моды уже установлены.")
                self.finished.emit(True)
                return

            self.log_message.emit(f"Найдено недостающих модов: {len(missing)}")
            total_missing = len(missing)

            for index, (row, entry) in enumerate(missing, start=1):
                if self._cancelled:
                    self.log_message.emit("Операция была остановлена.")
                    self.finished.emit(False)
                    return

                self.mod_status_changed.emit(row, "Скачивается")
                self.log_message.emit(f"Скачивание: {entry.name}")

                self._download_mod(
                    entry=entry,
                    destination=mods_dir / Path(entry.file).name,
                    completed_count=index - 1,
                    total_count=total_missing,
                )

                self.mod_status_changed.emit(row, "Установлен")
                self.progress_changed.emit(int((index / total_missing) * 100))
                self.log_message.emit(f"Готово: {entry.name}")

            self.progress_changed.emit(100)
            self.log_message.emit("Обновление модов завершено.")
            self.finished.emit(True)
        except (URLError, HTTPError, TimeoutError):
            message = "Не удалось проверить обновления"
            self.error_occurred.emit(message)
            self.log_message.emit(message)
            self.finished.emit(False)
        except Exception as exc:  # noqa: BLE001
            message = f"Ошибка: {exc}"
            self.error_occurred.emit(message)
            self.log_message.emit(message)
            self.finished.emit(False)

    def cancel(self) -> None:
        self._cancelled = True

    def _download_json(self, url: str) -> dict[str, Any]:
        request = Request(
            url,
            headers={
                "User-Agent": "Mod-Updater/1.0",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
        with urlopen(request, timeout=8) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload)

    def _parse_manifest(self, payload: dict[str, Any]) -> tuple[str, list[ModEntry]]:
        version = self._extract_version(payload)
        raw_mods = payload.get("mods")
        if raw_mods is None:
            raw_mods = payload.get("files", [])

        if not isinstance(raw_mods, Iterable) or isinstance(raw_mods, (str, bytes, dict)):
            raise ValueError("manifest.json содержит некорректный список модов")

        mods: list[ModEntry] = []
        for item in raw_mods:
            if isinstance(item, str):
                file_name = item
                display_name = Path(file_name).stem
            elif isinstance(item, dict):
                file_name = str(item.get("file", "")).strip()
                if not file_name:
                    continue
                display_name = str(
                    item.get("name")
                    or item.get("title")
                    or item.get("display_name")
                    or Path(file_name).stem
                )
            else:
                continue

            mods.append(ModEntry(name=display_name, file=file_name))

        if not mods:
            raise ValueError("manifest.json не содержит модов для установки")

        return version, mods

    def _extract_version(self, payload: dict[str, Any]) -> str:
        direct_version = payload.get("version")
        if direct_version is not None and str(direct_version).strip():
            return str(direct_version).strip()

        for key in ("modpack", "metadata", "manifest"):
            nested = payload.get(key)
            if isinstance(nested, dict):
                nested_version = nested.get("version")
                if nested_version is not None and str(nested_version).strip():
                    return str(nested_version).strip()

        return ""

    def _inspect_mods(
        self, mods: list[ModEntry], mods_dir: Path
    ) -> list[tuple[int, ModEntry]]:
        missing: list[tuple[int, ModEntry]] = []
        for index, entry in enumerate(mods):
            target = mods_dir / Path(entry.file).name
            if target.exists():
                self.mod_status_changed.emit(index, "Установлен")
            else:
                self.mod_status_changed.emit(index, "Отсутствует")
                missing.append((index, entry))
        return missing

    def _remove_extra_mods(self, mods: list[ModEntry], mods_dir: Path) -> None:
        expected_files = {Path(entry.file).name.lower() for entry in mods}
        removed_files: list[str] = []

        for file_path in mods_dir.iterdir():
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() != ".jar":
                continue
            if file_path.name.lower() in expected_files:
                continue

            file_path.unlink(missing_ok=True)
            removed_files.append(file_path.name)

        if removed_files:
            self.log_message.emit(
                f"Удалены лишние моды: {', '.join(sorted(removed_files))}"
            )

    def _download_mod(
        self, entry: ModEntry, destination: Path, completed_count: int, total_count: int
    ) -> None:
        request = Request(
            self._build_download_url(entry.file),
            headers={
                "User-Agent": "Mod-Updater/1.0",
                "Cache-Control": "no-cache",
            },
        )
        with urlopen(request, timeout=15) as response:
            file_size = int(response.headers.get("Content-Length", "0"))
            temp_fd, temp_name = tempfile.mkstemp(
                prefix="mod_updater_", suffix=".part", dir=str(destination.parent)
            )
            os.close(temp_fd)
            temp_path = Path(temp_name)

            current_bytes = 0
            try:
                with temp_path.open("wb") as handle:
                    while True:
                        chunk = response.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        handle.write(chunk)
                        current_bytes += len(chunk)
                        self._emit_progress(
                            current_bytes=current_bytes,
                            file_size=file_size,
                            completed_count=completed_count,
                            total_count=total_count,
                        )

                temp_path.replace(destination)
            finally:
                if temp_path.exists():
                    temp_path.unlink(missing_ok=True)

    def _emit_progress(
        self, current_bytes: int, file_size: int, completed_count: int, total_count: int
    ) -> None:
        if total_count <= 0:
            self.progress_changed.emit(0)
            return

        completed_share = completed_count / total_count
        current_file_share = 0.0
        if file_size > 0:
            current_file_share = (current_bytes / file_size) / total_count

        progress = int((completed_share + current_file_share) * 100)
        self.progress_changed.emit(max(0, min(progress, 100)))

    def _build_download_url(self, file_name: str) -> str:
        clean_path = file_name.lstrip("/").replace("\\", "/")
        return BASE_DOWNLOAD_URL + quote(clean_path)

    def _get_mods_dir(self) -> Path:
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / ".minecraft" / "mods"

        return Path.home() / "AppData" / "Roaming" / ".minecraft" / "mods"
