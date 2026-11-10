"""Tests for Excel workbook generation."""

from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import load_workbook

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.record import Record
from app.services.excel_service import ExcelGenerationError, generate_excel_report
import pytest


SAMPLE = [
    Record("Laptop", "Electronics", 2, 90000),
    Record("Mouse", "Accessories", 5, 2500),
]


def test_generate_excel_creates_workbook(tmp_path: Path) -> None:
    report = generate_excel_report(SAMPLE, output_dir=tmp_path)

    assert Path(report.filepath).exists()
    assert report.filename.endswith(".xlsx")
    assert report.record_count == 2
    assert report.grand_total == 92500
    assert report.status == "Completed"

    workbook = load_workbook(report.filepath)
    sheet = workbook.active
    assert sheet["A1"].value == "Report Studio"
    assert sheet["A10"].value == "#"
    assert sheet["B11"].value == "Laptop"
    assert sheet["D12"].value == 5


def test_generate_excel_rejects_empty_records(tmp_path: Path) -> None:
    with pytest.raises(ExcelGenerationError):
        generate_excel_report([], output_dir=tmp_path)


def test_generate_excel_avoids_duplicate_names(tmp_path: Path) -> None:
    first = generate_excel_report(SAMPLE, output_dir=tmp_path)
    # Force a collision by writing a second file with the same timestamp pattern
    # via calling again quickly; service should still produce a unique name.
    second = generate_excel_report(SAMPLE, output_dir=tmp_path)
    assert first.filename != second.filename or first.filepath != second.filepath
    assert Path(first.filepath).exists()
    assert Path(second.filepath).exists()


def test_generate_excel_unique_filename_with_forced_collision(tmp_path: Path) -> None:
    from datetime import datetime

    from app.services.excel_service import _unique_filename

    stamp = datetime(2026, 11, 10, 12, 0, 0)
    (tmp_path / "Report_Studio_20261110_120000.xlsx").write_text("taken", encoding="utf-8")
    (tmp_path / "Report_Studio_20261110_120000_1.xlsx").write_text("taken", encoding="utf-8")

    name = _unique_filename(tmp_path, stamp)
    assert name == "Report_Studio_20261110_120000_2.xlsx"


def test_generate_excel_includes_totals(tmp_path: Path) -> None:
    report = generate_excel_report(SAMPLE, output_dir=tmp_path)
    workbook = load_workbook(report.filepath)
    sheet = workbook.active

    # Header row is 10, two data rows occupy 11-12, totals start at 14.
    assert sheet["A14"].value == "Totals"
    assert sheet["A15"].value == "Total Quantity"
    assert sheet["B15"].value == 7
    assert sheet["A16"].value == "Grand Total"
    assert sheet["B16"].value == 92500
