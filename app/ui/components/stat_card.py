"""Clickable summary card used on Dashboard and report libraries."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class IconBadge(QWidget):
    """Rounded icon badge with a short letter mark."""

    def __init__(
        self,
        letter: str,
        background: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._letter = letter
        self._background = background
        self.setFixedSize(44, 44)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self._background))
        painter.drawRoundedRect(0, 0, 44, 44, 12, 12)

        painter.setPen(QColor("white"))
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._letter)
        painter.end()


class StatCard(QFrame):
    """Metric card with icon, value, label, and optional click action."""

    clicked = pyqtSignal()

    def __init__(
        self,
        title: str,
        value: str | int = 0,
        hint: str = "",
        icon_letter: str = "R",
        icon_color: str = "#356DE0",
        clickable: bool = True,
        compact: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("statCard")
        self._clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setProperty("clickable", "true")
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setProperty("clickable", "false")
        self._build_ui(title, value, hint, icon_letter, icon_color, compact)

    def _build_ui(
        self,
        title: str,
        value: str | int,
        hint: str,
        icon_letter: str,
        icon_color: str,
        compact: bool,
    ) -> None:
        layout = QHBoxLayout(self)
        margins = (16, 14, 16, 14) if compact else (20, 18, 20, 18)
        layout.setContentsMargins(*margins)
        layout.setSpacing(14 if compact else 16)

        badge = IconBadge(icon_letter, icon_color)
        if compact:
            badge.setFixedSize(36, 36)
        layout.addWidget(badge)

        text_column = QVBoxLayout()
        text_column.setSpacing(2)

        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("statValue")
        if compact:
            self.value_label.setStyleSheet("font-size: 22px; font-weight: 700;")

        self.title_label = QLabel(title)
        self.title_label.setObjectName("statLabel")

        self.hint_label = QLabel(hint)
        self.hint_label.setObjectName("statHint")
        self.hint_label.setWordWrap(True)
        self.hint_label.setVisible(bool(hint))

        text_column.addWidget(self.value_label)
        text_column.addWidget(self.title_label)
        text_column.addWidget(self.hint_label)
        layout.addLayout(text_column, stretch=1)

    def set_value(self, value: str | int) -> None:
        self.value_label.setText(str(value))

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
