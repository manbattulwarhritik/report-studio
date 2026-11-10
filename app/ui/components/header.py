"""Top content header with theme toggle and primary action."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class Header(QWidget):
    """Shared header used above every stacked screen."""

    new_report_clicked = pyqtSignal()
    theme_toggled = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._is_dark = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()

        self.theme_button = QPushButton("☀  Light")
        self.theme_button.setObjectName("themeToggle")
        self.theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_button.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_button)

        self.new_report_button = QPushButton("+  New Report")
        self.new_report_button.setObjectName("primaryButton")
        self.new_report_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_report_button.clicked.connect(self.new_report_clicked.emit)
        layout.addWidget(self.new_report_button)

    def _toggle_theme(self) -> None:
        self._is_dark = not self._is_dark
        if self._is_dark:
            self.theme_button.setText("☾  Dark")
        else:
            self.theme_button.setText("☀  Light")
        self.theme_toggled.emit(self._is_dark)

    def set_dark(self, is_dark: bool) -> None:
        self._is_dark = is_dark
        self.theme_button.setText("☾  Dark" if is_dark else "☀  Light")
