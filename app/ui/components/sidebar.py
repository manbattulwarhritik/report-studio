"""Fixed left navigation sidebar."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.theme import Theme


NAV_ITEMS = [
    ("dashboard", "Dashboard"),
    ("data_entry", "Data Entry"),
    ("excel_reports", "Excel Reports"),
    ("pdf_reports", "PDF Reports"),
    ("convert_pdf", "Convert to PDF"),
    ("history", "History"),
]


class BrandIcon(QWidget):
    """Simple blue bar-chart mark used in the brand header."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(36, 36)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(Theme.PRIMARY))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 36, 36, 10, 10)

        painter.setPen(QPen(QColor("white"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(10, 24, 10, 16)
        painter.drawLine(18, 24, 18, 10)
        painter.drawLine(26, 24, 26, 14)
        painter.end()


class Sidebar(QFrame):
    """Application sidebar with branding and navigation buttons."""

    navigate = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(230)
        self._buttons: dict[str, QPushButton] = {}
        self._active_key = "dashboard"
        self._build_ui()
        self.set_active("dashboard")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(8)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)
        brand_row.addWidget(BrandIcon())

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        title = QLabel("Report Studio")
        title.setObjectName("brandTitle")
        subtitle = QLabel("Excel & PDF Reports")
        subtitle.setObjectName("brandSubtitle")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        layout.addLayout(brand_row)
        layout.addSpacing(18)

        for key, label in NAV_ITEMS:
            button = QPushButton(f"  {label}")
            button.setObjectName("navButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setProperty("nav_key", key)
            button.clicked.connect(lambda checked=False, k=key: self._on_nav_clicked(k))
            self._buttons[key] = button
            layout.addWidget(button)

        layout.addStretch()

    def _on_nav_clicked(self, key: str) -> None:
        self.set_active(key)
        self.navigate.emit(key)

    def set_active(self, key: str) -> None:
        self._active_key = key
        for button_key, button in self._buttons.items():
            is_active = button_key == key
            button.setProperty("active", "true" if is_active else "false")
            button.style().unpolish(button)
            button.style().polish(button)
