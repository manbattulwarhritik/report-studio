"""Compact status pill used in tables."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget

from app.ui.theme import Theme


class StatusBadge(QLabel):
    """Rounded success/error status indicator."""

    def __init__(
        self,
        text: str = "Completed",
        success: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        prefix = "✓ " if success else "✕ "
        self.setText(f"{prefix}{text}")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg = Theme.SUCCESS_BG if success else "#FDECEC"
        fg = Theme.SUCCESS if success else Theme.ERROR
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border-radius: 10px;
                padding: 4px 10px;
                font-weight: 600;
            }}
            """
        )
