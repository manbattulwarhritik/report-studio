"""Minimal placeholder screens used until each milestone is built."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class PlaceholderScreen(QWidget):
    """Simple titled page so sidebar navigation works during early milestones."""

    def __init__(self, title: str, message: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        card = QFrame()
        card.setObjectName("placeholderCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)

        body = QLabel(message)
        body.setObjectName("pageSubtitle")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        card_layout.addWidget(body)
        layout.addWidget(card, stretch=1)
