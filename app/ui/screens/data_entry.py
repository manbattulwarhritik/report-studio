"""Data Entry screen for creating and editing sample records."""

from __future__ import annotations

from copy import deepcopy

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
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

from app.models.record import Record
from app.services.validation_service import CATEGORIES, validate_record
from app.ui import dialogs
from app.ui.components.stat_card import StatCard
from app.ui.theme import Theme
from app.utils.formatting import format_inr


class DataEntryScreen(QWidget):
    """Enter, edit, and summarize records before Excel generation."""

    generate_excel_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._records: list[Record] = []
        self._editing_index: int | None = None
        self._generating = False
        self._build_ui()
        self._refresh_table()
        self._update_totals()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        title = QLabel("Data Entry")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Add and manage records for your Excel report.")
        subtitle.setObjectName("pageSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(18, 16, 18, 16)
        form_layout.setSpacing(12)

        fields_row = QHBoxLayout()
        fields_row.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter item name")
        fields_row.addLayout(self._labeled_field("Name", self.name_input), stretch=2)

        self.category_input = QComboBox()
        self.category_input.addItem("Select category", "")
        for category in CATEGORIES:
            self.category_input.addItem(category, category)
        fields_row.addLayout(self._labeled_field("Category", self.category_input), stretch=2)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("e.g. 2")
        self.quantity_input.setClearButtonEnabled(True)
        fields_row.addLayout(self._labeled_field("Quantity", self.quantity_input), stretch=1)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("e.g. 90000")
        self.amount_input.setClearButtonEnabled(True)
        fields_row.addLayout(self._labeled_field("Amount", self.amount_input), stretch=1)

        form_layout.addLayout(fields_row)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)

        self.add_button = QPushButton("+  Add Record")
        self.add_button.setObjectName("primaryButton")
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.clicked.connect(self._on_add_or_update)
        buttons_row.addWidget(self.add_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.clicked.connect(self._on_clear_form)
        buttons_row.addWidget(self.clear_button)
        buttons_row.addStretch()
        form_layout.addLayout(buttons_row)
        root.addWidget(form_card)

        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(18, 16, 18, 16)
        table_layout.setSpacing(10)

        table_title = QLabel("Records")
        table_title.setObjectName("sectionTitle")
        table_layout.addWidget(table_title)

        self.records_table = QTableWidget(0, 6)
        self.records_table.setObjectName("recordsTable")
        self.records_table.setHorizontalHeaderLabels(
            ["#", "Name", "Category", "Quantity", "Amount", "Actions"]
        )
        self.records_table.verticalHeader().setVisible(False)
        self.records_table.setShowGrid(False)
        self.records_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.records_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.records_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.records_table.horizontalHeader().setStretchLastSection(True)
        self.records_table.setColumnWidth(0, 50)
        self.records_table.setColumnWidth(1, 180)
        self.records_table.setColumnWidth(2, 140)
        self.records_table.setColumnWidth(3, 100)
        self.records_table.setColumnWidth(4, 120)
        self.records_table.setMinimumHeight(240)
        table_layout.addWidget(self.records_table)
        root.addWidget(table_card, stretch=1)

        footer_row = QHBoxLayout()
        footer_row.setSpacing(12)

        self.total_records_card = StatCard(
            title="Total Records",
            value=0,
            icon_letter="R",
            icon_color=Theme.PRIMARY,
            clickable=False,
            compact=True,
        )
        self.total_quantity_card = StatCard(
            title="Total Quantity",
            value=0,
            icon_letter="Q",
            icon_color="#7C5CFC",
            clickable=False,
            compact=True,
        )
        self.grand_total_card = StatCard(
            title="Grand Total",
            value=format_inr(0),
            icon_letter="₹",
            icon_color=Theme.SUCCESS,
            clickable=False,
            compact=True,
        )
        self.grand_total_card.value_label.setObjectName("grandTotalValue")

        footer_row.addWidget(self.total_records_card, stretch=1)
        footer_row.addWidget(self.total_quantity_card, stretch=1)
        footer_row.addWidget(self.grand_total_card, stretch=1)

        self.generate_button = QPushButton("Generate Excel Report")
        self.generate_button.setObjectName("primaryButton")
        self.generate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_button.setMinimumHeight(48)
        self.generate_button.clicked.connect(self._on_generate_excel)
        footer_row.addWidget(self.generate_button)

        root.addLayout(footer_row)

    def _labeled_field(self, label_text: str, widget: QWidget) -> QVBoxLayout:
        column = QVBoxLayout()
        column.setSpacing(4)
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        column.addWidget(label)
        column.addWidget(widget)
        return column

    def get_records(self) -> list[Record]:
        """Return a copy of the current records for Excel generation."""
        return deepcopy(self._records)

    def _on_add_or_update(self) -> None:
        name = self.name_input.text()
        category = self.category_input.currentData()
        quantity_text = self.quantity_input.text().strip()
        amount_text = self.amount_input.text().strip().replace("₹", "").replace(",", "")

        result = validate_record(name, category, quantity_text, amount_text)
        if not result.ok:
            dialogs.warning(self, "Validation Error", result.message)
            return

        record = Record(
            name=name.strip(),
            category=str(category),
            quantity=int(quantity_text),
            amount=float(amount_text),
        )

        if self._editing_index is None:
            self._records.append(record)
        else:
            self._records[self._editing_index] = record

        self._on_clear_form()
        self._refresh_table()
        self._update_totals()

    def _on_clear_form(self) -> None:
        self._editing_index = None
        self.name_input.clear()
        self.category_input.setCurrentIndex(0)
        self.quantity_input.clear()
        self.amount_input.clear()
        self.add_button.setText("+  Add Record")

    def _on_edit_row(self, row_index: int) -> None:
        if row_index < 0 or row_index >= len(self._records):
            return

        record = self._records[row_index]
        self._editing_index = row_index
        self.name_input.setText(record.name)

        category_index = self.category_input.findData(record.category)
        self.category_input.setCurrentIndex(max(category_index, 0))
        self.quantity_input.setText(str(record.quantity))
        self.amount_input.setText(str(record.amount))
        self.add_button.setText("Update Record")
        self.name_input.setFocus()

    def _on_delete_row(self, row_index: int) -> None:
        if row_index < 0 or row_index >= len(self._records):
            return

        record = self._records[row_index]
        if not dialogs.question(
            self,
            "Delete Record",
            f"Delete '{record.name}' from the list?",
        ):
            return

        del self._records[row_index]

        if self._editing_index is not None:
            if self._editing_index == row_index:
                self._on_clear_form()
            elif self._editing_index > row_index:
                self._editing_index -= 1

        self._refresh_table()
        self._update_totals()

    def _on_generate_excel(self) -> None:
        if not self._records:
            dialogs.warning(
                self,
                "No Records",
                "Add at least one record before generating an Excel report.",
            )
            return
        self.generate_excel_requested.emit()

    def _refresh_table(self) -> None:
        self.records_table.setRowCount(0)
        self.records_table.setRowCount(len(self._records))

        for row_index, record in enumerate(self._records):
            values = [
                str(row_index + 1),
                record.name,
                record.category,
                str(record.quantity),
                format_inr(record.amount),
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if column_index in {0, 3, 4}:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
                    )
                self.records_table.setItem(row_index, column_index, item)

            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(4)

            edit_button = QPushButton("✎")
            edit_button.setObjectName("iconButton")
            edit_button.setToolTip("Edit")
            edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_button.clicked.connect(
                lambda checked=False, index=row_index: self._on_edit_row(index)
            )

            delete_button = QPushButton("🗑")
            delete_button.setObjectName("iconButton")
            delete_button.setProperty("danger", "true")
            delete_button.setToolTip("Delete")
            delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_button.clicked.connect(
                lambda checked=False, index=row_index: self._on_delete_row(index)
            )

            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            actions_layout.addStretch()
            self.records_table.setCellWidget(row_index, 5, actions)
            self.records_table.setRowHeight(row_index, 42)

    def _update_totals(self) -> None:
        total_records = len(self._records)
        total_quantity = sum(record.quantity for record in self._records)
        grand_total = sum(record.amount for record in self._records)

        self.total_records_card.set_value(total_records)
        self.total_quantity_card.set_value(total_quantity)
        self.grand_total_card.set_value(format_inr(grand_total))
        if not getattr(self, "_generating", False):
            self.generate_button.setEnabled(total_records > 0)

    def set_generating(self, busy: bool) -> None:
        """Disable generation controls while a background Excel job runs."""
        self._generating = busy
        self.generate_button.setEnabled((not busy) and bool(self._records))
        self.add_button.setEnabled(not busy)
        self.generate_button.setText(
            "Generating…" if busy else "Generate Excel Report"
        )
