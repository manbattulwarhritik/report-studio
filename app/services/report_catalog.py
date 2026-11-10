"""JSON catalogs for generated Excel and PDF reports."""

from __future__ import annotations

import json
from pathlib import Path

from app.models.report import ExcelReport, PdfReport
from app.utils.paths import excel_catalog_path, pdf_catalog_path


class ReportCatalog:
    """Persist and query Excel/PDF report metadata."""

    def __init__(
        self,
        catalog_path: Path | None = None,
        pdf_catalog_file: Path | None = None,
    ) -> None:
        self.catalog_path = Path(catalog_path) if catalog_path else excel_catalog_path()
        self.pdf_catalog_path = (
            Path(pdf_catalog_file) if pdf_catalog_file else pdf_catalog_path()
        )
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        self.pdf_catalog_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.catalog_path.exists():
            self._write_json(self.catalog_path, [])
        if not self.pdf_catalog_path.exists():
            self._write_json(self.pdf_catalog_path, [])

    # --- Excel ---

    def list_excel_reports(self) -> list[ExcelReport]:
        reports = self._read_excel_reports()
        existing: list[ExcelReport] = []
        changed = False

        for report in reports:
            if Path(report.filepath).exists():
                existing.append(report)
            else:
                changed = True

        if changed:
            self._write_excel_reports(existing)

        return sorted(existing, key=lambda item: item.generated_on, reverse=True)

    def add_report(self, report: ExcelReport) -> ExcelReport:
        reports = [item for item in self._read_excel_reports() if item.id != report.id]
        reports.append(report)
        self._write_excel_reports(reports)
        return report

    def get_report(self, report_id: str) -> ExcelReport | None:
        for report in self.list_excel_reports():
            if report.id == report_id:
                return report
        return None

    def delete_report(self, report_id: str) -> bool:
        reports = self._read_excel_reports()
        remaining: list[ExcelReport] = []
        deleted: ExcelReport | None = None

        for report in reports:
            if report.id == report_id:
                deleted = report
            else:
                remaining.append(report)

        if deleted is None:
            return False

        path = Path(deleted.filepath)
        if path.exists():
            path.unlink()

        self._write_excel_reports(remaining)
        return True

    def excel_count(self) -> int:
        return len(self.list_excel_reports())

    def completed_count(self) -> int:
        return sum(1 for report in self.list_excel_reports() if report.status == "Completed")

    # --- PDF ---

    def list_pdf_reports(self) -> list[PdfReport]:
        reports = self._read_pdf_reports()
        existing: list[PdfReport] = []
        changed = False

        for report in reports:
            if Path(report.filepath).exists():
                existing.append(report)
            else:
                changed = True

        if changed:
            self._write_pdf_reports(existing)

        return sorted(existing, key=lambda item: item.generated_on, reverse=True)

    def add_pdf_report(self, report: PdfReport) -> PdfReport:
        reports = [item for item in self._read_pdf_reports() if item.id != report.id]
        reports.append(report)
        self._write_pdf_reports(reports)
        return report

    def get_pdf_report(self, report_id: str) -> PdfReport | None:
        for report in self.list_pdf_reports():
            if report.id == report_id:
                return report
        return None

    def delete_pdf_report(self, report_id: str) -> bool:
        reports = self._read_pdf_reports()
        remaining: list[PdfReport] = []
        deleted: PdfReport | None = None

        for report in reports:
            if report.id == report_id:
                deleted = report
            else:
                remaining.append(report)

        if deleted is None:
            return False

        path = Path(deleted.filepath)
        if path.exists():
            path.unlink()

        self._write_pdf_reports(remaining)
        return True

    def pdf_count(self) -> int:
        return len(self.list_pdf_reports())

    def pdf_completed_count(self) -> int:
        return sum(1 for report in self.list_pdf_reports() if report.status == "Completed")

    # --- Internals ---

    def _read_excel_reports(self) -> list[ExcelReport]:
        reports: list[ExcelReport] = []
        for item in self._read_json(self.catalog_path):
            if isinstance(item, dict):
                try:
                    reports.append(ExcelReport.from_dict(item))
                except (KeyError, TypeError, ValueError):
                    continue
        return reports

    def _write_excel_reports(self, reports: list[ExcelReport]) -> None:
        self._write_json(self.catalog_path, [report.to_dict() for report in reports])

    def _read_pdf_reports(self) -> list[PdfReport]:
        reports: list[PdfReport] = []
        for item in self._read_json(self.pdf_catalog_path):
            if isinstance(item, dict):
                try:
                    reports.append(PdfReport.from_dict(item))
                except (KeyError, TypeError, ValueError):
                    continue
        return reports

    def _write_pdf_reports(self, reports: list[PdfReport]) -> None:
        self._write_json(self.pdf_catalog_path, [report.to_dict() for report in reports])

    def _read_json(self, path: Path) -> list:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return raw if isinstance(raw, list) else []

    def _write_json(self, path: Path, payload: list) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
