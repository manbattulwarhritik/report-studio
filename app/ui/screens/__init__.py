"""Screen widgets hosted by the main window stacked layout."""

from app.ui.screens.convert_pdf import ConvertPdfScreen
from app.ui.screens.dashboard import DashboardScreen
from app.ui.screens.data_entry import DataEntryScreen
from app.ui.screens.excel_preview import ExcelPreviewScreen
from app.ui.screens.excel_reports import ExcelReportsScreen
from app.ui.screens.history import HistoryScreen
from app.ui.screens.pdf_reports import PdfReportsScreen
from app.ui.screens.placeholder import PlaceholderScreen

__all__ = [
    "ConvertPdfScreen",
    "DashboardScreen",
    "DataEntryScreen",
    "ExcelPreviewScreen",
    "ExcelReportsScreen",
    "HistoryScreen",
    "PdfReportsScreen",
    "PlaceholderScreen",
]
