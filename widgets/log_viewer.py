"""Colored terminal-style log viewer."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class LogViewer(QWidget):
    """Displays timestamped TX/RX/ERROR/INFO messages."""

    COLORS = {
        "TX": QColor("#f1c40f"),
        "RX": QColor("#5dade2"),
        "ERROR": QColor("#ff6b6b"),
        "INFO": QColor("#9be564"),
    }

    def __init__(self) -> None:
        super().__init__()
        self.terminal = QTextEdit()
        self.terminal.setObjectName("terminal")
        self.terminal.setReadOnly(True)
        self.terminal.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.terminal.setMinimumHeight(260)
        self.terminal.setFontFamily("Consolas")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.terminal)

    def append(self, level: str, message: str) -> None:
        """Append a colored log line."""

        level = level.upper()
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        color = self.COLORS.get(level, QColor("#cfcfcf"))
        fmt = QTextCharFormat()
        fmt.setForeground(color)

        self.terminal.moveCursor(QTextCursor.MoveOperation.End)
        self.terminal.setCurrentCharFormat(fmt)
        self.terminal.insertPlainText(f"[{timestamp}] {level}: {message}\n")
        self.terminal.moveCursor(QTextCursor.MoveOperation.End)

    def clear(self) -> None:
        self.terminal.clear()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.key() == Qt.Key.Key_Escape:
            self.clear()
            return
        super().keyPressEvent(event)

