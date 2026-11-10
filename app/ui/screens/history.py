"""History screen showing application activity from local JSON storage."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.history_service import HistoryEntry
from app.ui.components.status_badge import StatusBadge


_KIND_ICONS = {
    "excel_generated": "📗",
    "excel_downloaded": "⬇",
    "excel_deleted": "🗑",
    "excel_opened": "👁",
    "pdf_converted": "📄",
    "pdf_downloaded": "⬇",
    "pdf_printed": "🖨",
    "pdf_deleted": "🗑",
    "pdf_opened": "👁",
    "excel_failed": "📗",
    "pdf_failed": "📄",
}


class HistoryScreen(QWidget):
    """Chronological log of generate, convert, download, print, and delete actions."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self.set_entries([])

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        title = QLabel("History")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Activity log for report generation, conversion, and file actions.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("tableCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)

        self.table = QTableWidget(0, 5)
        self.table.setObjectName("reportsTable")
        self.table.setHorizontalHeaderLabels(
            ["#", "Date & Time", "Activity", "Details", "Status"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 220)
        self.table.setColumnWidth(3, 280)
        card_layout.addWidget(self.table)

        self.empty_label = QLabel("No activity yet. Generate or convert a report to begin.")
        self.empty_label.setObjectName("pageSubtitle")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setVisible(False)
        card_layout.addWidget(self.empty_label)
        root.addWidget(card, stretch=1)

    def set_entries(self, entries: list[HistoryEntry]) -> None:
        self.table.setRowCount(0)

        if not entries:
            self.table.setVisible(False)
            self.empty_label.setVisible(True)
            return

        self.empty_label.setVisible(False)
        self.table.setVisible(True)
        self.table.setRowCount(len(entries))

        for row_index, entry in enumerate(entries):
            icon = _KIND_ICONS.get(entry.kind, "•")
            values = [
                str(row_index + 1),
                _format_timestamp(entry.timestamp),
                f"{icon}  {entry.activity}",
                entry.details,
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if column_index == 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter
                    )
                self.table.setItem(row_index, column_index, item)

            is_success = entry.status.lower() in {"success", "completed", "ok"}
            badge = StatusBadge(entry.status, success=is_success)
            wrapper = QWidget()
            wrapper_layout = QHBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(8, 4, 8, 4)
            wrapper_layout.addWidget(badge)
            wrapper_layout.addStretch()
            self.table.setCellWidget(row_index, 4, wrapper)
            self.table.setRowHeight(row_index, 44)


def _format_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return value
