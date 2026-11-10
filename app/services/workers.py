"""Background workers for long-running Report Studio tasks."""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from app.models.record import Record
from app.models.report import ExcelReport, PdfReport
from app.services.excel_service import ExcelGenerationError, generate_excel_report
from app.services.pdf_service import PdfConversionError, convert_excel_to_pdf


class ExcelGenerationWorker(QObject):
    """Generate an Excel workbook off the UI thread."""

    finished = pyqtSignal(object)  # ExcelReport
    failed = pyqtSignal(str)

    def __init__(self, records: list[Record]) -> None:
        super().__init__()
        self._records = list(records)

    def run(self) -> None:
        try:
            report: ExcelReport = generate_excel_report(self._records)
            self.finished.emit(report)
        except ExcelGenerationError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(f"Unexpected error while generating Excel: {exc}")


class PdfConversionWorker(QObject):
    """Convert an existing Excel workbook to PDF off the UI thread."""

    finished = pyqtSignal(object)  # PdfReport
    failed = pyqtSignal(str)

    def __init__(
        self,
        excel_report: ExcelReport,
        output_filename: str,
        orientation: str,
        page_size: str,
    ) -> None:
        super().__init__()
        self._excel_report = excel_report
        self._output_filename = output_filename
        self._orientation = orientation
        self._page_size = page_size

    def run(self) -> None:
        try:
            report: PdfReport = convert_excel_to_pdf(
                self._excel_report,
                output_filename=self._output_filename,
                orientation=self._orientation,
                page_size=self._page_size,
            )
            self.finished.emit(report)
        except PdfConversionError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(f"Unexpected error while converting to PDF: {exc}")
