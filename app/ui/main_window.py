"""Main application window with sidebar navigation and stacked screens."""

from __future__ import annotations

import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QThread, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.models.report import ExcelReport, PdfReport
from app.services.history_service import HistoryService
from app.services.report_catalog import ReportCatalog
from app.services.workers import ExcelGenerationWorker, PdfConversionWorker
from app.ui import dialogs
from app.ui.components.header import Header
from app.ui.components.progress_dialog import ProgressDialog
from app.ui.components.sidebar import Sidebar
from app.ui.screens.convert_pdf import ConvertPdfScreen
from app.ui.screens.dashboard import DashboardScreen
from app.ui.screens.data_entry import DataEntryScreen
from app.ui.screens.excel_preview import ExcelPreviewScreen
from app.ui.screens.excel_reports import ExcelReportsScreen
from app.ui.screens.history import HistoryScreen
from app.ui.screens.pdf_reports import PdfReportsScreen
from app.ui.theme import Theme


SCREEN_ORDER = [
    "dashboard",
    "data_entry",
    "excel_reports",
    "pdf_reports",
    "convert_pdf",
    "history",
    "excel_preview",
]


class MainWindow(QMainWindow):
    """Single-window shell hosting all Report Studio screens."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Report Studio")
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        self._is_dark = False
        self._screen_indexes = {key: index for index, key in enumerate(SCREEN_ORDER)}
        self._catalog = ReportCatalog()
        self._history = HistoryService()
        self._excel_thread: QThread | None = None
        self._excel_worker: ExcelGenerationWorker | None = None
        self._pdf_thread: QThread | None = None
        self._pdf_worker: PdfConversionWorker | None = None
        self._progress_dialog: ProgressDialog | None = None

        self._build_ui()
        self.apply_theme(dark=False)
        self._refresh_report_views()
        self.navigate_to("dashboard")

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralRoot")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.navigate.connect(self.navigate_to)
        root_layout.addWidget(self.sidebar)

        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 22, 28, 22)
        content_layout.setSpacing(18)

        self.header = Header()
        self.header.new_report_clicked.connect(lambda: self.navigate_to("data_entry"))
        self.header.theme_toggled.connect(self.apply_theme)
        content_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, stretch=1)
        root_layout.addWidget(content, stretch=1)

        self.dashboard = DashboardScreen()
        self.dashboard.open_excel_reports.connect(lambda: self.navigate_to("excel_reports"))
        self.dashboard.open_pdf_reports.connect(lambda: self.navigate_to("pdf_reports"))
        self.dashboard.open_history.connect(lambda: self.navigate_to("history"))
        self.stack.addWidget(self.dashboard)

        self.data_entry = DataEntryScreen()
        self.data_entry.generate_excel_requested.connect(self._on_generate_excel_requested)
        self.stack.addWidget(self.data_entry)

        self.excel_reports = ExcelReportsScreen()
        self.excel_reports.create_new_report.connect(lambda: self.navigate_to("data_entry"))
        self.excel_reports.preview_requested.connect(self._open_excel_preview)
        self.excel_reports.download_requested.connect(self._download_excel_report)
        self.excel_reports.delete_requested.connect(self._delete_excel_report)
        self.stack.addWidget(self.excel_reports)

        self.pdf_reports = PdfReportsScreen()
        self.pdf_reports.create_new_report.connect(lambda: self.navigate_to("data_entry"))
        self.pdf_reports.preview_requested.connect(self._preview_pdf_report)
        self.pdf_reports.download_requested.connect(self._download_pdf_report)
        self.pdf_reports.print_requested.connect(self._print_pdf_report)
        self.pdf_reports.delete_requested.connect(self._delete_pdf_report)
        self.stack.addWidget(self.pdf_reports)

        self.convert_pdf = ConvertPdfScreen()
        self.convert_pdf.convert_requested.connect(self._on_convert_pdf_requested)
        self.stack.addWidget(self.convert_pdf)

        self.history_screen = HistoryScreen()
        self.stack.addWidget(self.history_screen)

        self.excel_preview = ExcelPreviewScreen()
        self.excel_preview.back_requested.connect(lambda: self.navigate_to("excel_reports"))
        self.excel_preview.open_external_requested.connect(self._open_excel_external)
        self.excel_preview.download_requested.connect(self._download_excel_report)
        self.excel_preview.delete_requested.connect(self._delete_excel_report)
        self.stack.addWidget(self.excel_preview)

    def navigate_to(self, key: str) -> None:
        """Switch the stacked screen and sync the sidebar highlight."""
        index = self._screen_indexes.get(key)
        if index is None:
            return
        self.stack.setCurrentIndex(index)

        sidebar_key = "excel_reports" if key == "excel_preview" else key
        if sidebar_key in {
            "dashboard",
            "data_entry",
            "excel_reports",
            "pdf_reports",
            "convert_pdf",
            "history",
        }:
            self.sidebar.set_active(sidebar_key)

        if key in {"excel_reports", "pdf_reports", "excel_preview"}:
            self.header.new_report_button.setText("+  Create New Report")
        else:
            self.header.new_report_button.setText("+  New Report")

        if key == "convert_pdf":
            self.convert_pdf.set_excel_reports(self._catalog.list_excel_reports())
        if key in {"history", "dashboard"}:
            self._refresh_history_views()

    def apply_theme(self, dark: bool) -> None:
        """Apply the light or dark stylesheet to the whole window."""
        self._is_dark = dark
        stylesheet = Theme.dark_stylesheet() if dark else Theme.light_stylesheet()
        self.setStyleSheet(stylesheet)
        self.header.set_dark(dark)
        if self._progress_dialog is not None:
            self._progress_dialog.apply_theme(dark)

    def _ensure_progress_dialog(self) -> ProgressDialog:
        if self._progress_dialog is None:
            self._progress_dialog = ProgressDialog(self)
            self._progress_dialog.apply_theme(self._is_dark)
        return self._progress_dialog

    def _show_progress(self, title: str, message: str) -> None:
        dialog = self._ensure_progress_dialog()
        dialog.apply_theme(self._is_dark)
        dialog.show_progress(title, message)
        QApplication.processEvents()

    def _hide_progress(self) -> None:
        if self._progress_dialog is not None:
            self._progress_dialog.close_progress()

    def _refresh_report_views(self) -> None:
        excel_reports = self._catalog.list_excel_reports()
        pdf_reports = self._catalog.list_pdf_reports()
        self.excel_reports.set_reports(excel_reports)
        self.pdf_reports.set_reports(pdf_reports)
        self.convert_pdf.set_excel_reports(excel_reports)
        self.dashboard.set_stats(
            excel_count=len(excel_reports),
            pdf_count=len(pdf_reports),
        )
        self._refresh_history_views()

    def _refresh_history_views(self) -> None:
        entries = self._history.list_entries()
        self.history_screen.set_entries(entries)

        recent_rows: list[dict[str, str]] = []
        for entry in entries[:5]:
            recent_rows.append(
                {
                    "time": _format_clock(entry.timestamp),
                    "activity": entry.activity,
                    "file": entry.details,
                    "status": entry.status,
                }
            )
        self.dashboard.set_recent_activity(recent_rows)

    def _log_activity(
        self,
        activity: str,
        details: str,
        *,
        status: str = "Success",
        kind: str = "info",
    ) -> None:
        self._history.add(activity, details, status=status, kind=kind)
        self._refresh_history_views()

    # --- Excel generation ---

    def _on_generate_excel_requested(self) -> None:
        if self._excel_thread is not None and self._excel_thread.isRunning():
            dialogs.information(self, "Generation In Progress", "An Excel report is already being generated. Please wait.",
            )
            return

        records = self.data_entry.get_records()
        if not records:
            dialogs.warning(self, "No Records", "Add at least one record before generating an Excel report.",
            )
            return

        self.data_entry.set_generating(True)
        self._show_progress(
            "Generating Excel Report",
            "Creating your workbook. Please wait…",
        )
        self._excel_thread = QThread(self)
        self._excel_worker = ExcelGenerationWorker(records)
        self._excel_worker.moveToThread(self._excel_thread)

        self._excel_thread.started.connect(self._excel_worker.run)
        self._excel_worker.finished.connect(self._on_excel_generation_finished)
        self._excel_worker.failed.connect(self._on_excel_generation_failed)
        self._excel_worker.finished.connect(self._excel_thread.quit)
        self._excel_worker.failed.connect(self._excel_thread.quit)
        self._excel_thread.finished.connect(self._cleanup_excel_worker)

        self._excel_thread.start()

    def _on_excel_generation_finished(self, report: object) -> None:
        assert isinstance(report, ExcelReport)
        self._hide_progress()
        self._catalog.add_report(report)
        self.data_entry.set_generating(False)
        self._log_activity(
            "Excel report generated",
            report.filename,
            kind="excel_generated",
        )
        self._refresh_report_views()
        self.navigate_to("excel_reports")
        dialogs.success(
            self,
            "Excel Report Generated",
            f"Saved as {report.filename}\n\n{report.record_count} record(s) exported.",
        )

    def _on_excel_generation_failed(self, message: str) -> None:
        self._hide_progress()
        self.data_entry.set_generating(False)
        self._log_activity(
            "Excel generation failed",
            message,
            status="Failed",
            kind="excel_failed",
        )
        dialogs.critical(self, "Excel Generation Failed", message)

    def _cleanup_excel_worker(self) -> None:
        if self._excel_worker is not None:
            self._excel_worker.deleteLater()
            self._excel_worker = None
        if self._excel_thread is not None:
            self._excel_thread.deleteLater()
            self._excel_thread = None

    def _open_excel_preview(self, report_id: str) -> None:
        report = self._catalog.get_report(report_id)
        if report is None:
            dialogs.warning(self, "Missing Report", "That Excel report could not be found.")
            self._refresh_report_views()
            return
        self.excel_preview.set_report(report)
        self.navigate_to("excel_preview")

    def _open_excel_external(self, report_id: str) -> None:
        report = self._catalog.get_report(report_id)
        if report is None:
            dialogs.warning(self, "Missing Report", "That Excel report could not be found.")
            return
        path = Path(report.filepath)
        if not path.exists():
            dialogs.warning(self, "Missing File", "The Excel file is no longer on disk.")
            self._refresh_report_views()
            return
        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        if opened:
            self._log_activity(
                "Excel report opened",
                report.filename,
                kind="excel_opened",
            )
        else:
            dialogs.warning(self, "Unable to Open", "Could not open the workbook with the system default application.",
            )

    def _download_excel_report(self, report_id: str) -> None:
        report = self._catalog.get_report(report_id)
        if report is None:
            dialogs.warning(self, "Missing Report", "That Excel report could not be found.")
            return

        source = Path(report.filepath)
        if not source.exists():
            dialogs.warning(self, "Missing File", "The Excel file is no longer on disk.")
            self._refresh_report_views()
            return

        destination, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel Report As",
            report.filename,
            "Excel Workbook (*.xlsx)",
        )
        if not destination:
            return

        try:
            shutil.copy2(source, destination)
        except OSError as exc:
            self._log_activity(
                "Excel download failed",
                report.filename,
                status="Failed",
                kind="excel_downloaded",
            )
            dialogs.critical(self, "Download Failed", f"Could not save the file:\n{exc}")
            return

        self._log_activity(
            "Excel report downloaded",
            report.filename,
            kind="excel_downloaded",
        )
        dialogs.information(self, "Download Complete", f"Saved to:\n{destination}")

    def _delete_excel_report(self, report_id: str) -> None:
        report = self._catalog.get_report(report_id)
        if report is None:
            dialogs.warning(self, "Missing Report", "That Excel report could not be found.")
            self._refresh_report_views()
            return

        if not dialogs.question(
            self,
            "Delete Excel Report",
            f"Delete '{report.filename}'?\nThis cannot be undone.",
        ):
            return

        filename = report.filename
        self._catalog.delete_report(report_id)
        self._log_activity(
            "Excel report deleted",
            filename,
            kind="excel_deleted",
        )
        self._refresh_report_views()

        if self.stack.currentWidget() is self.excel_preview:
            self.navigate_to("excel_reports")

    # --- PDF conversion ---

    def _on_convert_pdf_requested(
        self,
        excel_id: str,
        output_filename: str,
        orientation: str,
        page_size: str,
    ) -> None:
        if self._pdf_thread is not None and self._pdf_thread.isRunning():
            dialogs.information(self, "Conversion In Progress", "A PDF conversion is already running. Please wait.",
            )
            return

        excel_report = self._catalog.get_report(excel_id)
        if excel_report is None:
            dialogs.warning(self, "Missing Excel Report", "The selected Excel workbook could not be found.",
            )
            self._refresh_report_views()
            return

        if not Path(excel_report.filepath).exists():
            dialogs.warning(self, "Missing Excel File", "The selected Excel file is no longer on disk.",
            )
            self._refresh_report_views()
            return

        self.convert_pdf.set_converting(True)
        self._show_progress(
            "Converting to PDF",
            f"Converting {excel_report.filename} with LibreOffice. Please wait…",
        )
        self._pdf_thread = QThread(self)
        self._pdf_worker = PdfConversionWorker(
            excel_report,
            output_filename=output_filename,
            orientation=orientation,
            page_size=page_size,
        )
        self._pdf_worker.moveToThread(self._pdf_thread)

        self._pdf_thread.started.connect(self._pdf_worker.run)
        self._pdf_worker.finished.connect(self._on_pdf_conversion_finished)
        self._pdf_worker.failed.connect(self._on_pdf_conversion_failed)
        self._pdf_worker.finished.connect(self._pdf_thread.quit)
        self._pdf_worker.failed.connect(self._pdf_thread.quit)
        self._pdf_thread.finished.connect(self._cleanup_pdf_worker)

        self._pdf_thread.start()

    def _on_pdf_conversion_finished(self, report: object) -> None:
        assert isinstance(report, PdfReport)
        self._hide_progress()
        self._catalog.add_pdf_report(report)
        self.convert_pdf.set_converting(False)
        self._log_activity(
            "Excel converted to PDF",
            f"{report.source_excel_filename} → {report.filename}",
            kind="pdf_converted",
        )
        self._refresh_report_views()
        self.navigate_to("pdf_reports")
        dialogs.success(
            self,
            "PDF Created",
            (
                f"Saved as {report.filename}\n\n"
                f"Source Excel: {report.source_excel_filename}\n"
                f"The original workbook was left unchanged."
            ),
        )

    def _on_pdf_conversion_failed(self, message: str) -> None:
        self._hide_progress()
        self.convert_pdf.set_converting(False)
        self._log_activity(
            "PDF conversion failed",
            message,
            status="Failed",
            kind="pdf_failed",
        )
        dialogs.critical(self, "PDF Conversion Failed", message)

    def _cleanup_pdf_worker(self) -> None:
        if self._pdf_worker is not None:
            self._pdf_worker.deleteLater()
            self._pdf_worker = None
        if self._pdf_thread is not None:
            self._pdf_thread.deleteLater()
            self._pdf_thread = None

    def _preview_pdf_report(self, report_id: str) -> None:
        report = self._catalog.get_pdf_report(report_id)
        if report is None:
            dialogs.warning(self, "Missing Report", "That PDF report could not be found.")
            self._refresh_report_views()
            return
        path = Path(report.filepath)
        if not path.exists():
            dialogs.warning(self, "Missing File", "The PDF file is no longer on disk.")
            self._refresh_report_views()
            return
        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        if opened:
            self._log_activity(
                "PDF report opened",
                report.filename,
                kind="pdf_opened",
            )
        else:
            dialogs.warning(self, "Unable to Open", "Could not open the PDF with the system default viewer.",
            )

    def _download_pdf_report(self, report_id: str) -> None:
        report = self._catalog.get_pdf_report(report_id)
        if report is None:
            dialogs.warning(self, "Missing Report", "That PDF report could not be found.")
            return

        source = Path(report.filepath)
        if not source.exists():
            dialogs.warning(self, "Missing File", "The PDF file is no longer on disk.")
            self._refresh_report_views()
            return

        destination, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report As",
            report.filename,
            "PDF Document (*.pdf)",
        )
        if not destination:
            return

        try:
            shutil.copy2(source, destination)
        except OSError as exc:
            self._log_activity(
                "PDF download failed",
                report.filename,
                status="Failed",
                kind="pdf_downloaded",
            )
            dialogs.critical(self, "Download Failed", f"Could not save the file:\n{exc}")
            return

        self._log_activity(
            "PDF report downloaded",
            report.filename,
            kind="pdf_downloaded",
        )
        dialogs.information(self, "Download Complete", f"Saved to:\n{destination}")

    def _print_pdf_report(self, report_id: str) -> None:
        report = self._catalog.get_pdf_report(report_id)
        if report is None:
            dialogs.warning(self, "Missing Report", "That PDF report could not be found.")
            return

        path = Path(report.filepath)
        if not path.exists():
            dialogs.warning(self, "Missing File", "The PDF file is no longer on disk.")
            self._refresh_report_views()
            return

        try:
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["open", "-p", str(path)], check=False)
            elif system == "Windows":
                subprocess.run(
                    ["powershell", "-Command", f'Start-Process -FilePath "{path}" -Verb Print'],
                    check=False,
                )
            else:
                subprocess.run(["lp", str(path)], check=False)
        except OSError as exc:
            self._log_activity(
                "PDF print failed",
                report.filename,
                status="Failed",
                kind="pdf_printed",
            )
            dialogs.critical(self, "Print Failed", f"Could not send the PDF to print:\n{exc}")
            return

        self._log_activity(
            "PDF report printed",
            report.filename,
            kind="pdf_printed",
        )
        dialogs.information(self, "Print", "The PDF was sent to the system print workflow.",
        )

    def _delete_pdf_report(self, report_id: str) -> None:
        report = self._catalog.get_pdf_report(report_id)
        if report is None:
            dialogs.warning(self, "Missing Report", "That PDF report could not be found.")
            self._refresh_report_views()
            return

        if not dialogs.question(
            self,
            "Delete PDF Report",
            f"Delete '{report.filename}'?\nThis cannot be undone.",
        ):
            return

        filename = report.filename
        self._catalog.delete_pdf_report(report_id)
        self._log_activity(
            "PDF report deleted",
            filename,
            kind="pdf_deleted",
        )
        self._refresh_report_views()


def _format_clock(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.strftime("%I:%M %p")
    except ValueError:
        return value
