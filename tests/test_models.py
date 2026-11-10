"""Unit tests for report and record models."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.record import Record
from app.models.report import ExcelReport, PdfReport
from app.services.history_service import HistoryEntry


def test_record_stores_fields() -> None:
    record = Record("Laptop", "Electronics", 2, 90000.0)
    assert record.name == "Laptop"
    assert record.category == "Electronics"
    assert record.quantity == 2
    assert record.amount == 90000.0


def test_excel_report_to_dict_round_trip() -> None:
    report = ExcelReport(
        id="excel-1",
        filename="demo.xlsx",
        filepath="/tmp/demo.xlsx",
        record_count=3,
        generated_on="2026-11-10T20:00:00",
        status="Completed",
        grand_total=135000.5,
    )
    restored = ExcelReport.from_dict(report.to_dict())
    assert restored == report


def test_excel_report_from_dict_defaults() -> None:
    report = ExcelReport.from_dict(
        {
            "id": "excel-2",
            "filename": "demo.xlsx",
            "filepath": "/tmp/demo.xlsx",
            "record_count": "4",
            "generated_on": "2026-11-10T20:00:00",
        }
    )
    assert report.status == "Completed"
    assert report.grand_total == 0.0
    assert report.record_count == 4


def test_excel_report_from_dict_requires_id() -> None:
    with pytest.raises(KeyError):
        ExcelReport.from_dict(
            {
                "filename": "demo.xlsx",
                "filepath": "/tmp/demo.xlsx",
                "record_count": 1,
                "generated_on": "2026-11-10T20:00:00",
            }
        )


def test_pdf_report_to_dict_round_trip() -> None:
    report = PdfReport(
        id="pdf-1",
        filename="demo.pdf",
        filepath="/tmp/demo.pdf",
        record_count=2,
        generated_on="2026-11-10T21:00:00",
        status="Completed",
        source_excel_id="excel-1",
        source_excel_filename="demo.xlsx",
        page_orientation="Landscape",
        page_size="Letter",
        grand_total=2500,
    )
    restored = PdfReport.from_dict(report.to_dict())
    assert restored == report


def test_pdf_report_from_dict_defaults() -> None:
    report = PdfReport.from_dict(
        {
            "id": "pdf-2",
            "filename": "demo.pdf",
            "filepath": "/tmp/demo.pdf",
            "record_count": 1,
            "generated_on": "2026-11-10T21:00:00",
        }
    )
    assert report.source_excel_id == ""
    assert report.page_orientation == "Portrait"
    assert report.page_size == "A4"
    assert report.grand_total == 0.0


def test_history_entry_from_dict_defaults() -> None:
    entry = HistoryEntry.from_dict(
        {
            "id": "h-1",
            "timestamp": "2026-11-10T21:00:00",
            "activity": "Excel generated",
        }
    )
    assert entry.details == ""
    assert entry.status == "Success"
    assert entry.kind == "info"
    assert entry.to_dict()["activity"] == "Excel generated"
