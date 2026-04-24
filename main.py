from __future__ import annotations

import sys
import ctypes
from pathlib import Path

from PySide6.QtCore import QThread, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from downloader import ModDownloaderWorker
from ui import MainWindow


APP_ID = "0x00000004.LauncherModsUpdater"


class ModUpdaterApp:
    def __init__(self) -> None:
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

        self.app = QApplication(sys.argv)
        icon_path = Path(__file__).resolve().parent / "Icon.ico"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))
        self.window = MainWindow()
        self.thread: QThread | None = None
        self.worker: ModDownloaderWorker | None = None

        self.window.refresh_button.clicked.connect(self.start_update)
        self.window.show()

        QTimer.singleShot(0, self.start_update)

    def start_update(self) -> None:
        if self.thread is not None and self.thread.isRunning():
            return

        self.window.set_busy(True)
        self.window.update_progress(0)
        self.window.append_log("=" * 42)
        self.window.append_log("Запуск проверки модов...")

        self.thread = QThread()
        self.worker = ModDownloaderWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.started.connect(
            lambda: self.window.set_info_message("Проверка обновлений...")
        )
        self.worker.manifest_loaded.connect(self.on_manifest_loaded)
        self.worker.mod_status_changed.connect(self.window.set_mod_status)
        self.worker.log_message.connect(self.window.append_log)
        self.worker.progress_changed.connect(self.window.update_progress)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._reset_thread)

        self.thread.start()

    def on_manifest_loaded(self, _version: str, mods: list[dict]) -> None:
        self.window.setWindowTitle("Launcher Mods Updater")
        self.window.populate_mods(mods)
        self.window.set_info_message("Список модов обновлён")

    def on_error(self, message: str) -> None:
        self.window.set_info_message(message)

    def on_finished(self, success: bool) -> None:
        if success:
            self.window.set_info_message("Проверка завершена")
        else:
            self.window.set_info_message("Не удалось проверить обновления")
        self.window.set_busy(False)

    def _reset_thread(self) -> None:
        self.thread = None
        self.worker = None

    def run(self) -> int:
        return self.app.exec()


if __name__ == "__main__":
    launcher = ModUpdaterApp()
    sys.exit(launcher.run())
