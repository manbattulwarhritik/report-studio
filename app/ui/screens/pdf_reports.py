"""PDF Reports library screen."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.report import PdfReport
from app.ui.components.stat_card import StatCard
from app.ui.components.status_badge import StatusBadge
from app.ui.theme import Theme


class PdfReportsScreen(QWidget):
    """Browse converted PDF documents."""

    create_new_report = pyqtSignal()
    preview_requested = pyqtSignal(str)
    download_requested = pyqtSignal(str)
    print_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reports: list[PdfReport] = []
        self._build_ui()
        self.set_reports([])

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        title = QLabel("PDF Reports")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Manage converted PDF documents.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        self.total_card = StatCard(
            title="Total Reports",
            value=0,
            icon_letter="P",
            icon_color="#D2463A",
            clickable=False,
            compact=True,
        )
        self.completed_card = StatCard(
            title="Completed",
            value=0,
            icon_letter="✓",
            icon_color=Theme.SUCCESS,
            clickable=False,
            compact=True,
        )
        cards_row.addWidget(self.total_card)
        cards_row.addWidget(self.completed_card)
        cards_row.addStretch()
        root.addLayout(cards_row)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Search by file name…")
        self.search_input.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self.search_input, stretch=1)

        self.create_button = QPushButton("+  Create New Report")
        self.create_button.setObjectName("primaryButton")
        self.create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_button.clicked.connect(self.create_new_report.emit)
        toolbar.addWidget(self.create_button)
        root.addLayout(toolbar)

        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(16, 14, 16, 14)

        self.table = QTableWidget(0, 5)
        self.table.setObjectName("reportsTable")
        self.table.setHorizontalHeaderLabels(
            ["File Name", "Records", "Generated On", "Status", "Actions"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 260)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 120)
        table_layout.addWidget(self.table)

        self.empty_label = QLabel("No PDF reports yet. Convert an Excel workbook first.")
        self.empty_label.setObjectName("pageSubtitle")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setVisible(False)
        table_layout.addWidget(self.empty_label)
        root.addWidget(table_card, stretch=1)

    def set_reports(self, reports: list[PdfReport]) -> None:
        self._reports = list(reports)
        self.total_card.set_value(len(self._reports))
        completed = sum(1 for report in self._reports if report.status == "Completed")
        self.completed_card.set_value(completed)
        self._apply_filter()

    def _apply_filter(self) -> None:
        query = self.search_input.text().strip().lower()
        if query:
            filtered = [r for r in self._reports if query in r.filename.lower()]
        else:
            filtered = list(self._reports)
        self._populate_table(filtered)

    def _populate_table(self, reports: list[PdfReport]) -> None:
        self.table.setRowCount(0)

        if not reports:
            self.table.setVisible(False)
            self.empty_label.setVisible(True)
            if self.search_input.text().strip():
                self.empty_label.setText("No reports match your search.")
            else:
                self.empty_label.setText("No PDF reports yet. Convert an Excel workbook first.")
            return

        self.empty_label.setVisible(False)
        self.table.setVisible(True)
        self.table.setRowCount(len(reports))

        for row_index, report in enumerate(reports):
            values = [
                report.filename,
                str(report.record_count),
                _format_timestamp(report.generated_on),
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if column_index == 1:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter
                    )
                self.table.setItem(row_index, column_index, item)

            is_success = report.status.lower() in {"completed", "success"}
            badge = StatusBadge(report.status, success=is_success)
            badge_wrap = QWidget()
            badge_layout = QHBoxLayout(badge_wrap)
            badge_layout.setContentsMargins(8, 4, 8, 4)
            badge_layout.addWidget(badge)
            badge_layout.addStretch()
            self.table.setCellWidget(row_index, 3, badge_wrap)

            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(4)

            preview_btn = QPushButton("👁")
            preview_btn.setObjectName("iconButton")
            preview_btn.setToolTip("Preview")
            preview_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            preview_btn.clicked.connect(
                lambda checked=False, report_id=report.id: self.preview_requested.emit(report_id)
            )

            download_btn = QPushButton("⬇")
            download_btn.setObjectName("iconButton")
            download_btn.setToolTip("Download / Save As")
            download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            download_btn.clicked.connect(
                lambda checked=False, report_id=report.id: self.download_requested.emit(report_id)
            )

            print_btn = QPushButton("🖨")
            print_btn.setObjectName("iconButton")
            print_btn.setToolTip("Print")
            print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            print_btn.clicked.connect(
                lambda checked=False, report_id=report.id: self.print_requested.emit(report_id)
            )

            delete_btn = QPushButton("🗑")
            delete_btn.setObjectName("iconButton")
            delete_btn.setProperty("danger", "true")
            delete_btn.setToolTip("Delete")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(
                lambda checked=False, report_id=report.id: self.delete_requested.emit(report_id)
            )

            actions_layout.addWidget(preview_btn)
            actions_layout.addWidget(download_btn)
            actions_layout.addWidget(print_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            self.table.setCellWidget(row_index, 4, actions)
            self.table.setRowHeight(row_index, 44)


def _format_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return value
