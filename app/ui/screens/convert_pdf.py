"""Convert an existing Excel workbook to PDF."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.report import ExcelReport
from app.services.pdf_service import PAGE_SIZES


class ConvertPdfScreen(QWidget):
    """Select a generated Excel file and convert it with LibreOffice."""

    convert_requested = pyqtSignal(str, str, str, str)
    # excel_id, output_filename, orientation, page_size

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reports: list[ExcelReport] = []
        self._selected_id: str | None = None
        self._excel_buttons: dict[str, QRadioButton] = {}
        self._excel_rows: dict[str, QFrame] = {}
        self._converting = False
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        title = QLabel("Convert to PDF")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Convert an existing Excel workbook into a PDF document.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        columns = QHBoxLayout()
        columns.setSpacing(16)

        # Left: Excel selection
        left = QFrame()
        left.setObjectName("formCard")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(18, 16, 18, 16)
        left_layout.setSpacing(10)

        left_title = QLabel("Select Excel Report")
        left_title.setObjectName("sectionTitle")
        left_layout.addWidget(left_title)

        self.excel_button_group = QButtonGroup(self)
        self.excel_button_group.setExclusive(True)

        self.excel_scroll = QScrollArea()
        self.excel_scroll.setObjectName("excelSelectList")
        self.excel_scroll.setWidgetResizable(True)
        self.excel_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.excel_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.excel_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.list_container = QWidget()
        self.list_container.setObjectName("excelSelectContainer")
        self.excel_list_layout = QVBoxLayout(self.list_container)
        self.excel_list_layout.setContentsMargins(4, 4, 4, 4)
        self.excel_list_layout.setSpacing(8)
        self.excel_list_layout.addStretch()
        self.excel_scroll.setWidget(self.list_container)
        left_layout.addWidget(self.excel_scroll, stretch=1)

        self.empty_excel_label = QLabel("No Excel reports available. Generate one first.")
        self.empty_excel_label.setObjectName("pageSubtitle")
        self.empty_excel_label.setWordWrap(True)
        left_layout.addWidget(self.empty_excel_label)

        columns.addWidget(left, stretch=1)

        # Right: settings + preview
        right = QFrame()
        right.setObjectName("formCard")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(18, 16, 18, 16)
        right_layout.setSpacing(12)

        right_title = QLabel("Conversion Settings")
        right_title.setObjectName("sectionTitle")
        right_layout.addWidget(right_title)

        filename_label = QLabel("Output PDF Filename")
        filename_label.setObjectName("fieldLabel")
        right_layout.addWidget(filename_label)
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("e.g. Sales_Report.pdf")
        right_layout.addWidget(self.filename_input)

        orientation_label = QLabel("Page Orientation")
        orientation_label.setObjectName("fieldLabel")
        right_layout.addWidget(orientation_label)
        orientation_row = QHBoxLayout()
        self.portrait_radio = QRadioButton("Portrait")
        self.landscape_radio = QRadioButton("Landscape")
        self.portrait_radio.setChecked(True)
        orientation_row.addWidget(self.portrait_radio)
        orientation_row.addWidget(self.landscape_radio)
        orientation_row.addStretch()
        right_layout.addLayout(orientation_row)

        size_label = QLabel("Page Size")
        size_label.setObjectName("fieldLabel")
        right_layout.addWidget(size_label)
        self.page_size_input = QComboBox()
        for size in PAGE_SIZES:
            self.page_size_input.addItem(size)
        right_layout.addWidget(self.page_size_input)

        preview_card = QFrame()
        preview_card.setObjectName("tableCard")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(14, 14, 14, 14)
        preview_layout.setSpacing(8)

        preview_title = QLabel("Conversion Preview")
        preview_title.setObjectName("sectionTitle")
        preview_layout.addWidget(preview_title)

        flow = QHBoxLayout()
        self.source_preview = QLabel("Excel")
        self.source_preview.setObjectName("statLabel")
        self.source_preview.setWordWrap(True)
        arrow = QLabel("→")
        arrow.setObjectName("pageSubtitle")
        self.target_preview = QLabel("PDF")
        self.target_preview.setObjectName("statLabel")
        self.target_preview.setWordWrap(True)
        flow.addWidget(self.source_preview)
        flow.addWidget(arrow)
        flow.addWidget(self.target_preview)
        flow.addStretch()
        preview_layout.addLayout(flow)

        self.preview_hint = QLabel(
            "Select an Excel workbook to convert. The original file will not be changed."
        )
        self.preview_hint.setObjectName("pageSubtitle")
        self.preview_hint.setWordWrap(True)
        preview_layout.addWidget(self.preview_hint)
        right_layout.addWidget(preview_card)
        right_layout.addStretch()

        columns.addWidget(right, stretch=1)
        root.addLayout(columns, stretch=1)

        self.convert_button = QPushButton("Convert Selected Excel to PDF")
        self.convert_button.setObjectName("primaryButton")
        self.convert_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_button.setMinimumHeight(46)
        self.convert_button.clicked.connect(self._on_convert_clicked)
        root.addWidget(self.convert_button)

        self.filename_input.textChanged.connect(self._update_preview_labels)
        self.portrait_radio.toggled.connect(lambda _checked: self._update_preview_labels())
        self.landscape_radio.toggled.connect(lambda _checked: self._update_preview_labels())
        self.page_size_input.currentTextChanged.connect(lambda _text: self._update_preview_labels())

    def set_excel_reports(self, reports: list[ExcelReport]) -> None:
        self._reports = list(reports)
        previous = self._selected_id

        while self.excel_list_layout.count():
            item = self.excel_list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self._excel_buttons.clear()
        self._excel_rows.clear()
        for button in self.excel_button_group.buttons():
            self.excel_button_group.removeButton(button)

        if not self._reports:
            self.empty_excel_label.setVisible(True)
            self._selected_id = None
            self.convert_button.setEnabled(False)
            self._update_preview_labels()
            return

        self.empty_excel_label.setVisible(False)
        for report in self._reports:
            row = QFrame()
            row.setObjectName("excelSelectRow")
            row.setProperty("selected", "false")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 10, 12, 10)
            row_layout.setSpacing(10)

            button = QRadioButton()
            button.setObjectName("excelSelectRadio")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.toggled.connect(
                lambda checked, report_id=report.id: self._on_excel_toggled(report_id, checked)
            )

            text_column = QVBoxLayout()
            text_column.setSpacing(2)
            name_label = QLabel(report.filename)
            name_label.setObjectName("excelSelectName")
            name_label.setWordWrap(True)
            date_label = QLabel(_format_timestamp(report.generated_on))
            date_label.setObjectName("excelSelectDate")
            date_label.setWordWrap(True)
            text_column.addWidget(name_label)
            text_column.addWidget(date_label)

            row_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignTop)
            row_layout.addLayout(text_column, stretch=1)

            # Clicking the row selects the radio.
            row.mousePressEvent = (  # type: ignore[method-assign]
                lambda event, btn=button: btn.setChecked(True) or None
            )

            self.excel_button_group.addButton(button)
            self._excel_buttons[report.id] = button
            self._excel_rows[report.id] = row
            self.excel_list_layout.addWidget(row)

        self.excel_list_layout.addStretch()

        select_id = previous if previous in self._excel_buttons else self._reports[0].id
        self._excel_buttons[select_id].setChecked(True)
        self._sync_row_selection(select_id)
        self.convert_button.setEnabled(not self._converting)

    def set_converting(self, busy: bool) -> None:
        self._converting = busy
        enabled = (not busy) and bool(self._reports) and bool(self._selected_id)
        self.convert_button.setEnabled(enabled)
        self.convert_button.setText(
            "Converting…" if busy else "Convert Selected Excel to PDF"
        )
        self.filename_input.setEnabled(not busy)
        self.portrait_radio.setEnabled(not busy)
        self.landscape_radio.setEnabled(not busy)
        self.page_size_input.setEnabled(not busy)
        for button in self._excel_buttons.values():
            button.setEnabled(not busy)

    def _on_excel_toggled(self, report_id: str, checked: bool) -> None:
        if not checked:
            return
        self._selected_id = report_id
        self._sync_row_selection(report_id)
        report = next((item for item in self._reports if item.id == report_id), None)
        if report is not None:
            # Always suggest a matching PDF name when selection changes.
            stem = report.filename.rsplit(".", 1)[0]
            self.filename_input.setText(f"{stem}.pdf")
        self._update_preview_labels()

    def _sync_row_selection(self, selected_id: str) -> None:
        for report_id, row in self._excel_rows.items():
            is_selected = report_id == selected_id
            row.setProperty("selected", "true" if is_selected else "false")
            row.style().unpolish(row)
            row.style().polish(row)

    def _update_preview_labels(self) -> None:
        report = next((item for item in self._reports if item.id == self._selected_id), None)
        if report is None:
            self.source_preview.setText("Excel")
            self.target_preview.setText("PDF")
            self.preview_hint.setText(
                "Select an Excel workbook to convert. The original file will not be changed."
            )
            return

        output_name = self.filename_input.text().strip() or f"{report.filename.rsplit('.', 1)[0]}.pdf"
        if not output_name.lower().endswith(".pdf"):
            output_name = f"{output_name}.pdf"

        self.source_preview.setText(report.filename)
        self.target_preview.setText(output_name)
        orientation = "Landscape" if self.landscape_radio.isChecked() else "Portrait"
        page_size = self.page_size_input.currentText()
        self.preview_hint.setText(
            f"Convert {report.filename} → {output_name} "
            f"({orientation}, {page_size}). Source Excel is preserved."
        )

    def _on_convert_clicked(self) -> None:
        if not self._selected_id:
            return
        output_name = self.filename_input.text().strip()
        orientation = "Landscape" if self.landscape_radio.isChecked() else "Portrait"
        page_size = self.page_size_input.currentText()
        self.convert_requested.emit(self._selected_id, output_name, orientation, page_size)


def _format_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return value
