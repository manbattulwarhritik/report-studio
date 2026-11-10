"""Tests for the Excel and PDF report catalogs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.report import ExcelReport, PdfReport
from app.services.report_catalog import ReportCatalog


def _sample_report(tmp_path: Path, name: str = "demo.xlsx") -> ExcelReport:
    filepath = tmp_path / name
    filepath.write_text("placeholder", encoding="utf-8")
    return ExcelReport(
        id="abc-123",
        filename=name,
        filepath=str(filepath),
        record_count=5,
        generated_on="2026-11-10T20:00:00",
        status="Completed",
        grand_total=135000,
    )


def _sample_pdf(tmp_path: Path, name: str = "demo.pdf") -> PdfReport:
    filepath = tmp_path / name
    filepath.write_bytes(b"%PDF-1.4 minimal content for tests")
    return PdfReport(
        id="pdf-1",
        filename=name,
        filepath=str(filepath),
        record_count=2,
        generated_on="2026-11-10T21:00:00",
        status="Completed",
        source_excel_id="excel-1",
        source_excel_filename="demo.xlsx",
        page_orientation="Portrait",
        page_size="A4",
        grand_total=100,
    )


def test_catalog_add_list_delete(tmp_path: Path) -> None:
    catalog = ReportCatalog(catalog_path=tmp_path / "excel_catalog.json")
    report = _sample_report(tmp_path)

    catalog.add_report(report)
    listed = catalog.list_excel_reports()
    assert len(listed) == 1
    assert listed[0].filename == "demo.xlsx"
    assert catalog.get_report("abc-123") is not None
    assert catalog.excel_count() == 1
    assert catalog.completed_count() == 1

    assert catalog.delete_report("abc-123") is True
    assert catalog.list_excel_reports() == []
    assert not (tmp_path / "demo.xlsx").exists()


def test_catalog_delete_missing_returns_false(tmp_path: Path) -> None:
    catalog = ReportCatalog(catalog_path=tmp_path / "excel_catalog.json")
    assert catalog.delete_report("does-not-exist") is False
    assert catalog.delete_pdf_report("does-not-exist") is False


def test_catalog_replaces_report_with_same_id(tmp_path: Path) -> None:
    catalog = ReportCatalog(catalog_path=tmp_path / "excel_catalog.json")
    first = _sample_report(tmp_path, "first.xlsx")
    second = ExcelReport(
        id=first.id,
        filename="second.xlsx",
        filepath=str(tmp_path / "second.xlsx"),
        record_count=1,
        generated_on="2026-11-10T22:00:00",
        status="Completed",
        grand_total=10,
    )
    (tmp_path / "second.xlsx").write_text("updated", encoding="utf-8")
    catalog.add_report(first)
    catalog.add_report(second)
    listed = catalog.list_excel_reports()
    assert len(listed) == 1
    assert listed[0].filename == "second.xlsx"


def test_catalog_prunes_missing_files(tmp_path: Path) -> None:
    catalog = ReportCatalog(catalog_path=tmp_path / "excel_catalog.json")
    report = ExcelReport(
        id="missing-1",
        filename="gone.xlsx",
        filepath=str(tmp_path / "gone.xlsx"),
        record_count=1,
        generated_on="2026-11-10T20:00:00",
        status="Completed",
        grand_total=10,
    )
    catalog.add_report(report)
    assert catalog.list_excel_reports() == []


def test_catalog_skips_corrupt_excel_entries(tmp_path: Path) -> None:
    catalog_path = tmp_path / "excel_catalog.json"
    catalog_path.write_text(
        json.dumps(
            [
                {"not": "a report"},
                {
                    "id": "ok-1",
                    "filename": "ok.xlsx",
                    "filepath": str(tmp_path / "ok.xlsx"),
                    "record_count": 1,
                    "generated_on": "2026-11-10T20:00:00",
                    "status": "Completed",
                    "grand_total": 10,
                },
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "ok.xlsx").write_text("ok", encoding="utf-8")
    catalog = ReportCatalog(catalog_path=catalog_path)
    listed = catalog.list_excel_reports()
    assert len(listed) == 1
    assert listed[0].id == "ok-1"


def test_pdf_catalog_lists_newest_first_and_counts(tmp_path: Path) -> None:
    catalog = ReportCatalog(
        catalog_path=tmp_path / "excel.json",
        pdf_catalog_file=tmp_path / "pdf.json",
    )
    older = _sample_pdf(tmp_path, "older.pdf")
    older.id = "pdf-old"
    older.generated_on = "2026-11-10T20:00:00"
    newer = _sample_pdf(tmp_path, "newer.pdf")
    newer.id = "pdf-new"
    newer.generated_on = "2026-11-10T22:00:00"

    catalog.add_pdf_report(older)
    catalog.add_pdf_report(newer)

    listed = catalog.list_pdf_reports()
    assert [item.id for item in listed] == ["pdf-new", "pdf-old"]
    assert catalog.pdf_count() == 2
    assert catalog.pdf_completed_count() == 2
    assert catalog.get_pdf_report("pdf-new") is not None


def test_pdf_catalog_prunes_missing_files(tmp_path: Path) -> None:
    catalog = ReportCatalog(
        catalog_path=tmp_path / "excel.json",
        pdf_catalog_file=tmp_path / "pdf.json",
    )
    report = PdfReport(
        id="missing-pdf",
        filename="gone.pdf",
        filepath=str(tmp_path / "gone.pdf"),
        record_count=1,
        generated_on="2026-11-10T20:00:00",
        status="Completed",
        source_excel_id="excel-1",
        source_excel_filename="demo.xlsx",
        page_orientation="Portrait",
        page_size="A4",
    )
    catalog.add_pdf_report(report)
    assert catalog.list_pdf_reports() == []
