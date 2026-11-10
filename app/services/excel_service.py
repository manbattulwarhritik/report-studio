"""Excel workbook generation with OpenPyXL."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.models.record import Record
from app.models.report import ExcelReport
from app.utils.paths import excel_output_dir


class ExcelGenerationError(Exception):
    """Raised when a workbook cannot be created or saved."""


def generate_excel_report(
    records: list[Record],
    output_dir: Path | None = None,
) -> ExcelReport:
    """
    Create a branded Excel workbook from the given records.

    Saves under output/excel by default and returns catalog metadata.
    """
    if not records:
        raise ExcelGenerationError("Cannot generate an Excel report with no records.")

    target_dir = Path(output_dir) if output_dir is not None else excel_output_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now()
    filename = _unique_filename(target_dir, generated_at)
    filepath = target_dir / filename

    try:
        workbook = _build_workbook(records, generated_at)
        workbook.save(filepath)
    except Exception as exc:  # noqa: BLE001 - surface a clear service error
        raise ExcelGenerationError(f"Failed to generate Excel report: {exc}") from exc

    grand_total = sum(record.amount for record in records)
    return ExcelReport(
        id=str(uuid.uuid4()),
        filename=filename,
        filepath=str(filepath.resolve()),
        record_count=len(records),
        generated_on=generated_at.isoformat(timespec="seconds"),
        status="Completed",
        grand_total=float(grand_total),
    )


def _unique_filename(target_dir: Path, generated_at: datetime) -> str:
    base = f"Report_Studio_{generated_at.strftime('%Y%m%d_%H%M%S')}"
    candidate = f"{base}.xlsx"
    if not (target_dir / candidate).exists():
        return candidate

    suffix = 1
    while True:
        candidate = f"{base}_{suffix}.xlsx"
        if not (target_dir / candidate).exists():
            return candidate
        suffix += 1


def _build_workbook(records: list[Record], generated_at: datetime) -> Workbook:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sales Report"

    primary_fill = PatternFill("solid", fgColor="356DE0")
    header_fill = PatternFill("solid", fgColor="E8EEF9")
    totals_fill = PatternFill("solid", fgColor="E8F8F0")
    white_font = Font(name="Calibri", bold=True, color="FFFFFF", size=16)
    title_font = Font(name="Calibri", bold=True, size=14, color="17243A")
    label_font = Font(name="Calibri", bold=True, size=11, color="17243A")
    body_font = Font(name="Calibri", size=11, color="17243A")
    muted_font = Font(name="Calibri", size=10, color="6B7A90")
    thin = Border(
        left=Side(style="thin", color="D0D7E2"),
        right=Side(style="thin", color="D0D7E2"),
        top=Side(style="thin", color="D0D7E2"),
        bottom=Side(style="thin", color="D0D7E2"),
    )

    # Branding header
    sheet.merge_cells("A1:E1")
    sheet["A1"] = "Report Studio"
    sheet["A1"].font = white_font
    sheet["A1"].fill = primary_fill
    sheet["A1"].alignment = Alignment(horizontal="left", vertical="center")
    sheet.row_dimensions[1].height = 28

    sheet.merge_cells("A2:E2")
    sheet["A2"] = "Excel Sales Report"
    sheet["A2"].font = title_font
    sheet["A2"].alignment = Alignment(horizontal="left", vertical="center")

    # Report info section
    sheet["A4"] = "Report Information"
    sheet["A4"].font = title_font
    sheet.merge_cells("A4:B4")

    sheet["A5"] = "Generated On"
    sheet["B5"] = generated_at.strftime("%d %b %Y, %I:%M %p")
    sheet["A6"] = "Total Records"
    sheet["B6"] = len(records)
    sheet["A7"] = "Status"
    sheet["B7"] = "Completed"

    for row in range(5, 8):
        sheet[f"A{row}"].font = label_font
        sheet[f"B{row}"].font = body_font

    # Data table
    table_start = 9
    sheet[f"A{table_start}"] = "Records"
    sheet[f"A{table_start}"].font = title_font
    sheet.merge_cells(f"A{table_start}:E{table_start}")

    headers = ["#", "Name", "Category", "Quantity", "Amount"]
    header_row = table_start + 1
    for col_index, header in enumerate(headers, start=1):
        cell = sheet.cell(row=header_row, column=col_index, value=header)
        cell.font = label_font
        cell.fill = header_fill
        cell.border = thin
        cell.alignment = Alignment(horizontal="center", vertical="center")

    data_start = header_row + 1
    for index, record in enumerate(records, start=1):
        row = data_start + index - 1
        values = [index, record.name, record.category, record.quantity, record.amount]
        for col_index, value in enumerate(values, start=1):
            cell = sheet.cell(row=row, column=col_index, value=value)
            cell.font = body_font
            cell.border = thin
            if col_index in {1, 4}:
                cell.alignment = Alignment(horizontal="center")
            if col_index == 5:
                cell.number_format = '₹#,##0.00'
                cell.alignment = Alignment(horizontal="right")

    data_end = data_start + len(records) - 1

    # Totals section
    totals_row = data_end + 2
    sheet[f"A{totals_row}"] = "Totals"
    sheet[f"A{totals_row}"].font = title_font

    quantity_total = sum(record.quantity for record in records)
    amount_total = sum(record.amount for record in records)

    sheet[f"A{totals_row + 1}"] = "Total Quantity"
    sheet[f"B{totals_row + 1}"] = quantity_total
    sheet[f"A{totals_row + 2}"] = "Grand Total"
    sheet[f"B{totals_row + 2}"] = amount_total
    sheet[f"B{totals_row + 2}"].number_format = '₹#,##0.00'

    for offset in (1, 2):
        for col in ("A", "B"):
            cell = sheet[f"{col}{totals_row + offset}"]
            cell.fill = totals_fill
            cell.border = thin
            cell.font = label_font if col == "A" else body_font

    footer_row = totals_row + 4
    sheet[f"A{footer_row}"] = "Generated by Report Studio — Excel & PDF Reports"
    sheet[f"A{footer_row}"].font = muted_font
    sheet.merge_cells(f"A{footer_row}:E{footer_row}")

    widths = {1: 8, 2: 22, 3: 16, 4: 12, 5: 14}
    for col_index, width in widths.items():
        sheet.column_dimensions[get_column_letter(col_index)].width = width

    return workbook
