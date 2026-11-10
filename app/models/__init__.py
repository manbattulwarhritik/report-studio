"""Domain models for Report Studio."""

from app.models.record import Record
from app.models.report import ExcelReport, PdfReport

__all__ = ["Record", "ExcelReport", "PdfReport"]
