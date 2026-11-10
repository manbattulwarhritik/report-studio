"""In-app Excel report preview (metadata and file actions)."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models.report import ExcelReport
from app.ui.components.status_badge import StatusBadge
from app.utils.formatting import format_inr


class ExcelPreviewScreen(QWidget):
    """Show workbook metadata and actions without rendering spreadsheet cells."""

    back_requested = pyqtSignal()
    open_external_requested = pyqtSignal(str)
    download_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._report: ExcelReport | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        top_row = QHBoxLayout()
        self.back_button = QPushButton("←  Back to Excel Reports")
        self.back_button.setObjectName("linkButton")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.clicked.connect(self.back_requested.emit)
        top_row.addWidget(self.back_button)
        top_row.addStretch()
        root.addLayout(top_row)

        title = QLabel("Excel Preview")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Report details and file actions. Open the workbook externally to view cells.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("tableCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(18)

        header = QHBoxLayout()
        self.filename_label = QLabel("—")
        self.filename_label.setObjectName("sectionTitle")
        header.addWidget(self.filename_label)
        header.addStretch()
        self.status_container = QHBoxLayout()
        header.addLayout(self.status_container)
        card_layout.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(12)

        self.generated_value = QLabel("—")
        self.records_value = QLabel("—")
        self.total_value = QLabel("—")
        self.total_value.setObjectName("grandTotalValue")
        self.path_value = QLabel("—")
        self.path_value.setWordWrap(True)
        self.path_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        grid.addWidget(self._meta_label("Generated On"), 0, 0)
        grid.addWidget(self.generated_value, 0, 1)
        grid.addWidget(self._meta_label("Records"), 1, 0)
        grid.addWidget(self.records_value, 1, 1)
        grid.addWidget(self._meta_label("Grand Total"), 2, 0)
        grid.addWidget(self.total_value, 2, 1)
        grid.addWidget(self._meta_label("File Path"), 3, 0)
        grid.addWidget(self.path_value, 3, 1)
        card_layout.addLayout(grid)

        note = QLabel(
            "This preview shows report metadata only. Use Open Externally to view the spreadsheet "
            "in Excel, Numbers, or LibreOffice."
        )
        note.setObjectName("pageSubtitle")
        note.setWordWrap(True)
        card_layout.addWidget(note)

        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.open_button = QPushButton("Open Externally")
        self.open_button.setObjectName("primaryButton")
        self.open_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_button.clicked.connect(self._emit_open)

        self.download_button = QPushButton("Download / Save As")
        self.download_button.setObjectName("secondaryButton")
        self.download_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_button.clicked.connect(self._emit_download)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("secondaryButton")
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.clicked.connect(self._emit_delete)

        actions.addWidget(self.open_button)
        actions.addWidget(self.download_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()
        card_layout.addLayout(actions)

        root.addWidget(card)
        root.addStretch()

    def _meta_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def set_report(self, report: ExcelReport) -> None:
        self._report = report
        self.filename_label.setText(report.filename)
        self.generated_value.setText(_format_timestamp(report.generated_on))
        self.records_value.setText(str(report.record_count))
        self.total_value.setText(format_inr(report.grand_total))
        self.path_value.setText(report.filepath)

        while self.status_container.count():
            item = self.status_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        is_success = report.status.lower() in {"completed", "success"}
        self.status_container.addWidget(StatusBadge(report.status, success=is_success))

    def _emit_open(self) -> None:
        if self._report is not None:
            self.open_external_requested.emit(self._report.id)

    def _emit_download(self) -> None:
        if self._report is not None:
            self.download_requested.emit(self._report.id)

    def _emit_delete(self) -> None:
        if self._report is not None:
            self.delete_requested.emit(self._report.id)


def _format_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return value
