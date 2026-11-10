"""Dashboard overview screen."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.ui.components.stat_card import StatCard
from app.ui.components.status_badge import StatusBadge


class DashboardScreen(QWidget):
    """Application overview: report counts and recent activity."""

    open_excel_reports = pyqtSignal()
    open_pdf_reports = pyqtSignal()
    open_history = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self.set_stats(excel_count=0, pdf_count=0)
        self.set_recent_activity([])

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(18)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Overview of generated Excel and PDF reports.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.excel_card = StatCard(
            title="Excel Reports",
            value=0,
            hint="Total generated workbooks.",
            icon_letter="X",
            icon_color="#217346",
        )
        self.excel_card.clicked.connect(self.open_excel_reports.emit)

        self.pdf_card = StatCard(
            title="PDF Reports",
            value=0,
            hint="Total generated documents.",
            icon_letter="P",
            icon_color="#D2463A",
        )
        self.pdf_card.clicked.connect(self.open_pdf_reports.emit)

        cards_row.addWidget(self.excel_card)
        cards_row.addWidget(self.pdf_card)
        root.addLayout(cards_row)

        activity_card = QFrame()
        activity_card.setObjectName("activityCard")
        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setContentsMargins(18, 16, 18, 16)
        activity_layout.setSpacing(10)

        header_row = QHBoxLayout()
        section_title = QLabel("Recent Activity")
        section_title.setObjectName("sectionTitle")
        header_row.addWidget(section_title)
        header_row.addStretch()

        self.view_all_button = QPushButton("View All")
        self.view_all_button.setObjectName("linkButton")
        self.view_all_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_all_button.clicked.connect(self.open_history.emit)
        header_row.addWidget(self.view_all_button)
        activity_layout.addLayout(header_row)

        self.activity_table = QTableWidget(0, 4)
        self.activity_table.setObjectName("activityTable")
        self.activity_table.setHorizontalHeaderLabels(["Time", "Activity", "File", "Status"])
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.setShowGrid(False)
        self.activity_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.activity_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        self.activity_table.setColumnWidth(0, 140)
        self.activity_table.setColumnWidth(1, 220)
        self.activity_table.setColumnWidth(2, 260)
        self.activity_table.setMinimumHeight(220)
        activity_layout.addWidget(self.activity_table)

        self.empty_label = QLabel("No recent activity yet. Generate a report to see it here.")
        self.empty_label.setObjectName("pageSubtitle")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setVisible(False)
        activity_layout.addWidget(self.empty_label)

        root.addWidget(activity_card, stretch=1)

    def set_stats(self, excel_count: int, pdf_count: int) -> None:
        """Update the summary cards. Called by the main window as data becomes available."""
        self.excel_card.set_value(excel_count)
        self.pdf_card.set_value(pdf_count)

    def set_recent_activity(self, rows: list[dict[str, str]]) -> None:
        """
        Populate the recent activity table.

        Expected row keys: time, activity, file, status
        """
        self.activity_table.setRowCount(0)

        if not rows:
            self.activity_table.setVisible(False)
            self.empty_label.setVisible(True)
            return

        self.empty_label.setVisible(False)
        self.activity_table.setVisible(True)
        self.activity_table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            values = [
                row.get("time", ""),
                row.get("activity", ""),
                row.get("file", ""),
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.activity_table.setItem(row_index, column_index, item)

            status_text = row.get("status", "Success")
            is_success = status_text.lower() in {"success", "completed", "ok"}
            badge = StatusBadge(status_text, success=is_success)
            wrapper = QWidget()
            wrapper_layout = QHBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(8, 4, 8, 4)
            wrapper_layout.addWidget(badge)
            wrapper_layout.addStretch()
            self.activity_table.setCellWidget(row_index, 3, wrapper)
            self.activity_table.setRowHeight(row_index, 44)
