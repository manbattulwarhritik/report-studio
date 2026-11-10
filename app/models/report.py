"""Report metadata models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ExcelReport:
    """Metadata for a generated Excel workbook."""

    id: str
    filename: str
    filepath: str
    record_count: int
    generated_on: str
    status: str
    grand_total: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExcelReport:
        return cls(
            id=str(data["id"]),
            filename=str(data["filename"]),
            filepath=str(data["filepath"]),
            record_count=int(data["record_count"]),
            generated_on=str(data["generated_on"]),
            status=str(data.get("status", "Completed")),
            grand_total=float(data.get("grand_total", 0)),
        )


@dataclass
class PdfReport:
    """Metadata for a PDF converted from an Excel workbook."""

    id: str
    filename: str
    filepath: str
    record_count: int
    generated_on: str
    status: str
    source_excel_id: str
    source_excel_filename: str
    page_orientation: str
    page_size: str
    grand_total: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PdfReport:
        return cls(
            id=str(data["id"]),
            filename=str(data["filename"]),
            filepath=str(data["filepath"]),
            record_count=int(data["record_count"]),
            generated_on=str(data["generated_on"]),
            status=str(data.get("status", "Completed")),
            source_excel_id=str(data.get("source_excel_id", "")),
            source_excel_filename=str(data.get("source_excel_filename", "")),
            page_orientation=str(data.get("page_orientation", "Portrait")),
            page_size=str(data.get("page_size", "A4")),
            grand_total=float(data.get("grand_total", 0)),
        )
