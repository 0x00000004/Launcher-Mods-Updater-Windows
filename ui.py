from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGraphicsOpacityEffect,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._animated_value = 0.0
        self._animation = QPropertyAnimation(self, b"animatedValue", self)
        self._animation.setDuration(350)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setRange(0, 100)
        self.setTextVisible(True)
        self.setFormat("%p%")

    def get_animated_value(self) -> float:
        return self._animated_value

    def set_animated_value(self, value: float) -> None:
        self._animated_value = value
        self.setValue(int(value))

    animatedValue = Property(float, get_animated_value, set_animated_value)

    def animate_to(self, value: int) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._animated_value)
        self._animation.setEndValue(float(value))
        self._animation.start()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Launcher Mods Updater")
        icon_path = Path(__file__).resolve().parent / "Icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(980, 720)
        self._fade_animations: list[QPropertyAnimation] = []
        self._setup_ui()
        self._apply_styles()
        QTimer.singleShot(120, self.play_intro)

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(18)

        self.header_card = QWidget()
        header_layout = QVBoxLayout(self.header_card)
        header_layout.setContentsMargins(24, 22, 24, 22)
        header_layout.setSpacing(6)

        self.developer_label = QLabel(
            'Разработчик: <a href="https://github.com/0x00000004">0x00000004</a>'
        )
        self.developer_label.setObjectName("developerLabel")
        self.developer_label.setTextFormat(Qt.TextFormat.RichText)
        self.developer_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.developer_label.setOpenExternalLinks(True)

        self.title_label = QLabel("Launcher Mods Updater")
        self.title_label.setObjectName("titleLabel")
        self.info_label = QLabel("Проверка обновлений...")
        self.info_label.setObjectName("infoLabel")

        header_layout.addWidget(self.developer_label, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.info_label)
        root_layout.addWidget(self.header_card)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(16)

        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setFixedHeight(18)
        controls_row.addWidget(self.progress_bar, 1)

        self.refresh_button = QPushButton("Обновить моды")
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setFixedWidth(190)
        controls_row.addWidget(self.refresh_button)
        root_layout.addLayout(controls_row)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Название", "Статус"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        root_layout.addWidget(self.table, 1)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Лог загрузки появится здесь...")
        self.log_box.setMinimumHeight(170)
        root_layout.addWidget(self.log_box)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background: #f0f0f0;
            }
            QWidget {
                color: #1f1f1f;
                font-family: "Segoe UI";
                font-size: 14px;
            }
            #titleLabel {
                font-size: 24px;
                font-weight: 600;
                color: #111111;
            }
            #developerLabel {
                font-size: 11px;
                color: #5a5a5a;
            }
            #developerLabel a {
                color: #005a9e;
                text-decoration: none;
            }
            #developerLabel a:hover {
                text-decoration: underline;
            }
            #infoLabel {
                color: #5a5a5a;
                font-size: 13px;
            }
            QWidget#header_card, QTableWidget, QTextEdit, QProgressBar {
                background: #ffffff;
                border: 1px solid #cfcfcf;
                border-radius: 0;
            }
            QPushButton {
                background-color: #e1e1e1;
                color: #111111;
                border: 1px solid #adadad;
                border-radius: 0;
                font-weight: 500;
                padding: 8px 16px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #eaf3fc;
                border: 1px solid #0078d7;
            }
            QPushButton:pressed {
                background-color: #cfe8ff;
                border: 1px solid #005a9e;
            }
            QPushButton:disabled {
                background-color: #f3f3f3;
                color: #8a8a8a;
                border: 1px solid #d8d8d8;
            }
            QProgressBar {
                background: #ffffff;
                padding: 1px;
                text-align: center;
                color: #1f1f1f;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
            }
            QHeaderView::section {
                background: #f3f3f3;
                color: #1f1f1f;
                border: 1px solid #d9d9d9;
                padding: 8px;
                font-weight: 600;
            }
            QTableWidget {
                gridline-color: #e4e4e4;
                alternate-background-color: #f9f9f9;
                selection-background-color: #cfe8ff;
                selection-color: #111111;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTextEdit {
                padding: 10px;
                color: #1f1f1f;
                background: #ffffff;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 14px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                border: 1px solid #b0b0b0;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: #f0f0f0;
            }
            QTextEdit, QTableWidget {
                border-top: 1px solid #d6d6d6;
            }
            QTableCornerButton::section {
                background: #f3f3f3;
                border: 1px solid #d9d9d9;
            }
            QToolTip {
                background: #ffffff;
                color: #111111;
                border: 1px solid #adadad;
                min-height: 24px;
            }
            """
        )
        self.header_card.setObjectName("header_card")

    def play_intro(self) -> None:
        self._fade_animations.clear()
        for delay, widget in enumerate(
            (self.header_card, self.progress_bar, self.table, self.log_box)
        ):
            effect = QGraphicsOpacityEffect(widget)
            effect.setOpacity(0.0)
            widget.setGraphicsEffect(effect)

            animation = QPropertyAnimation(effect, b"opacity", self)
            animation.setDuration(700)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            def start_animation(anim: QPropertyAnimation = animation) -> None:
                anim.start()

            QTimer.singleShot(120 * delay, start_animation)
            self._fade_animations.append(animation)

    def populate_mods(self, mods: list[dict[str, Any]]) -> None:
        self.table.setRowCount(len(mods))
        for row, mod in enumerate(mods):
            name_item = QTableWidgetItem(str(mod.get("name", "Unknown")))
            status_item = QTableWidgetItem("Проверка...")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, status_item)

    def set_mod_status(self, row: int, status: str) -> None:
        item = self.table.item(row, 1)
        if item is None:
            item = QTableWidgetItem()
            self.table.setItem(row, 1, item)
        item.setText(status)

        color_map = {
            "Установлен": "#22c55e",
            "Отсутствует": "#f59e0b",
            "Скачивается": "#38bdf8",
        }
        item.setForeground(QColor(color_map.get(status, "#1f1f1f")))

    def set_info_message(self, message: str) -> None:
        self.info_label.setText(message)

    def append_log(self, message: str) -> None:
        self.log_box.append(message)

    def set_busy(self, busy: bool) -> None:
        self.refresh_button.setDisabled(busy)
        if busy:
            self.set_info_message("Проверка обновлений...")

    def update_progress(self, value: int) -> None:
        self.progress_bar.animate_to(value)
