"""Tests for PDF conversion helpers and LibreOffice conversion."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.record import Record
from app.models.report import ExcelReport
from app.services.excel_service import generate_excel_report
from app.services.pdf_service import (
    PdfConversionError,
    _normalize_pdf_filename,
    _unique_pdf_name,
    _validate_pdf,
    convert_excel_to_pdf,
    find_soffice,
)
from app.services.report_catalog import ReportCatalog


def test_normalize_pdf_filename() -> None:
    assert _normalize_pdf_filename("Sales Report", "fallback") == "Sales_Report.pdf"
    assert _normalize_pdf_filename("out.pdf", "fallback") == "out.pdf"
    assert _normalize_pdf_filename("", "Report_Studio").endswith(".pdf")
    assert _normalize_pdf_filename("weird@name!.pdf", "fallback") == "weird_name_.pdf"


def test_unique_pdf_name_adds_suffix(tmp_path: Path) -> None:
    (tmp_path / "report.pdf").write_bytes(b"%PDF-")
    (tmp_path / "report_1.pdf").write_bytes(b"%PDF-")
    assert _unique_pdf_name(tmp_path, "report.pdf") == "report_2.pdf"


def test_validate_pdf_rejects_non_pdf(tmp_path: Path) -> None:
    bad = tmp_path / "bad.pdf"
    bad.write_text("not a pdf", encoding="utf-8")
    with pytest.raises(PdfConversionError):
        _validate_pdf(bad)


def test_validate_pdf_rejects_tiny_pdf(tmp_path: Path) -> None:
    tiny = tmp_path / "tiny.pdf"
    tiny.write_bytes(b"%PDF-")
    with pytest.raises(PdfConversionError, match="empty or corrupt"):
        _validate_pdf(tiny)


def test_convert_rejects_missing_source(tmp_path: Path) -> None:
    report = ExcelReport(
        id="excel-1",
        filename="missing.xlsx",
        filepath=str(tmp_path / "missing.xlsx"),
        record_count=1,
        generated_on="2026-11-10T20:00:00",
        status="Completed",
        grand_total=10,
    )
    with pytest.raises(PdfConversionError, match="Source Excel file was not found"):
        convert_excel_to_pdf(report, output_filename="out", output_dir=tmp_path)


def test_convert_rejects_invalid_page_options(tmp_path: Path) -> None:
    excel_path = tmp_path / "demo.xlsx"
    excel_path.write_text("placeholder", encoding="utf-8")
    report = ExcelReport(
        id="excel-1",
        filename="demo.xlsx",
        filepath=str(excel_path),
        record_count=1,
        generated_on="2026-11-10T20:00:00",
        status="Completed",
        grand_total=10,
    )

    with pytest.raises(PdfConversionError, match="Orientation"):
        convert_excel_to_pdf(
            report,
            output_filename="out",
            orientation="Diagonal",
            output_dir=tmp_path,
        )

    with pytest.raises(PdfConversionError, match="Page size"):
        convert_excel_to_pdf(
            report,
            output_filename="out",
            page_size="Tabloid",
            output_dir=tmp_path,
        )


def test_convert_excel_to_pdf_and_preserve_source(tmp_path: Path) -> None:
    try:
        find_soffice()
    except PdfConversionError:
        pytest.skip("LibreOffice soffice not available")

    excel_dir = tmp_path / "excel"
    pdf_dir = tmp_path / "pdf"
    excel_dir.mkdir()
    pdf_dir.mkdir()

    excel = generate_excel_report(
        [Record("Laptop", "Electronics", 2, 90000)],
        output_dir=excel_dir,
    )
    source_path = Path(excel.filepath)
    assert source_path.exists()

    pdf = convert_excel_to_pdf(
        excel,
        output_filename="sales_summary",
        orientation="Landscape",
        page_size="A4",
        output_dir=pdf_dir,
    )

    assert Path(pdf.filepath).exists()
    assert pdf.filename.endswith(".pdf")
    assert pdf.source_excel_id == excel.id
    assert pdf.source_excel_filename == excel.filename
    assert pdf.page_orientation == "Landscape"
    assert pdf.page_size == "A4"
    assert source_path.exists()  # source preserved after conversion
    with Path(pdf.filepath).open("rb") as handle:
        assert handle.read(5) == b"%PDF-"


def test_pdf_catalog_round_trip(tmp_path: Path) -> None:
    catalog = ReportCatalog(
        catalog_path=tmp_path / "excel.json",
        pdf_catalog_file=tmp_path / "pdf.json",
    )
    pdf_file = tmp_path / "demo.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 minimal")

    from app.models.report import PdfReport

    report = PdfReport(
        id="pdf-1",
        filename="demo.pdf",
        filepath=str(pdf_file),
        record_count=2,
        generated_on="2026-11-10T21:00:00",
        status="Completed",
        source_excel_id="excel-1",
        source_excel_filename="demo.xlsx",
        page_orientation="Portrait",
        page_size="A4",
        grand_total=100,
    )
    catalog.add_pdf_report(report)
    assert catalog.pdf_count() == 1
    assert catalog.get_pdf_report("pdf-1") is not None
    assert catalog.delete_pdf_report("pdf-1") is True
    assert catalog.pdf_count() == 0
    assert not pdf_file.exists()
