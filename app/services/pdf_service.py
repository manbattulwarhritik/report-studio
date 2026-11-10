"""Excel-to-PDF conversion via LibreOffice in headless mode."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.page import PageMargins

from app.models.report import ExcelReport, PdfReport
from app.utils.paths import pdf_output_dir


PAGE_SIZES = ("A4", "Letter", "Legal")
ORIENTATIONS = ("Portrait", "Landscape")

_PAPER_SIZE_CODES = {
    "Letter": 1,
    "Legal": 5,
    "A4": 9,
}

_SOFFICE_CANDIDATES = (
    "/opt/homebrew/bin/soffice",
    "/usr/local/bin/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "soffice",
)


class PdfConversionError(Exception):
    """Raised when an Excel workbook cannot be converted to PDF."""


def find_soffice() -> str:
    """Return the LibreOffice soffice executable path."""
    for candidate in _SOFFICE_CANDIDATES:
        path = Path(candidate)
        if candidate == "soffice":
            resolved = shutil.which("soffice")
            if resolved:
                return resolved
        elif path.exists():
            return str(path)
    raise PdfConversionError(
        "LibreOffice was not found. Install LibreOffice or ensure `soffice` is on PATH."
    )


def convert_excel_to_pdf(
    excel_report: ExcelReport,
    output_filename: str,
    orientation: str = "Portrait",
    page_size: str = "A4",
    output_dir: Path | None = None,
    soffice_path: str | None = None,
) -> PdfReport:
    """
    Convert an existing Excel workbook to PDF.

    The source workbook is never modified or deleted. Page size/orientation are
    applied to a temporary copy before LibreOffice headless conversion.
    """
    source = Path(excel_report.filepath)
    if not source.exists():
        raise PdfConversionError(f"Source Excel file was not found:\n{source}")

    orientation = orientation.strip().title()
    page_size = page_size.strip()
    if orientation not in ORIENTATIONS:
        raise PdfConversionError("Orientation must be Portrait or Landscape.")
    if page_size not in PAGE_SIZES:
        raise PdfConversionError("Page size must be A4, Letter, or Legal.")

    target_dir = Path(output_dir) if output_dir is not None else pdf_output_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    pdf_name = _normalize_pdf_filename(output_filename, source.stem)
    pdf_name = _unique_pdf_name(target_dir, pdf_name)
    destination = target_dir / pdf_name

    soffice = soffice_path or find_soffice()
    generated_at = datetime.now()

    with tempfile.TemporaryDirectory(prefix="report_studio_pdf_") as tmp:
        tmp_dir = Path(tmp)
        prepared = tmp_dir / source.name
        _prepare_workbook_copy(source, prepared, orientation=orientation, page_size=page_size)

        try:
            completed = subprocess.run(
                [
                    soffice,
                    "--headless",
                    "--nologo",
                    "--nofirststartwizard",
                    "--norestore",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(tmp_dir),
                    str(prepared),
                ],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise PdfConversionError(
                "LibreOffice timed out while converting the workbook to PDF."
            ) from exc
        except OSError as exc:
            raise PdfConversionError(f"Could not start LibreOffice: {exc}") from exc

        produced = prepared.with_suffix(".pdf")
        if not produced.exists():
            # LibreOffice sometimes alters the basename slightly; pick any PDF in tmp.
            pdfs = list(tmp_dir.glob("*.pdf"))
            if not pdfs:
                details = (completed.stderr or completed.stdout or "").strip()
                message = "LibreOffice did not produce a PDF file."
                if details:
                    message = f"{message}\n\n{details}"
                raise PdfConversionError(message)
            produced = pdfs[0]

        _validate_pdf(produced)
        shutil.copy2(produced, destination)

    if not destination.exists():
        raise PdfConversionError("PDF conversion finished but the output file is missing.")

    # Source Excel must still exist after a successful conversion.
    if not source.exists():
        raise PdfConversionError(
            "Conversion reported success but the source Excel file is missing."
        )

    return PdfReport(
        id=str(uuid.uuid4()),
        filename=pdf_name,
        filepath=str(destination.resolve()),
        record_count=excel_report.record_count,
        generated_on=generated_at.isoformat(timespec="seconds"),
        status="Completed",
        source_excel_id=excel_report.id,
        source_excel_filename=excel_report.filename,
        page_orientation=orientation,
        page_size=page_size,
        grand_total=excel_report.grand_total,
    )


def _prepare_workbook_copy(
    source: Path,
    destination: Path,
    orientation: str,
    page_size: str,
) -> None:
    workbook = load_workbook(source)
    paper_code = _PAPER_SIZE_CODES[page_size]
    orient = "portrait" if orientation == "Portrait" else "landscape"

    for sheet in workbook.worksheets:
        sheet.page_setup.orientation = orient
        sheet.page_setup.paperSize = paper_code
        sheet.page_setup.fitToPage = True
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0
        sheet.page_margins = PageMargins(
            left=0.5,
            right=0.5,
            top=0.5,
            bottom=0.5,
            header=0.3,
            footer=0.3,
        )
        sheet.print_title_rows = "1:2"

    workbook.save(destination)


def _normalize_pdf_filename(requested: str, fallback_stem: str) -> str:
    name = (requested or "").strip() or fallback_stem
    name = Path(name).name
    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"
    # Keep filesystem-safe characters.
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_", ".", " "} else "_" for ch in name)
    cleaned = cleaned.strip().replace(" ", "_")
    return cleaned or f"{fallback_stem}.pdf"


def _unique_pdf_name(target_dir: Path, filename: str) -> str:
    candidate = filename
    if not (target_dir / candidate).exists():
        return candidate

    stem = Path(filename).stem
    suffix = 1
    while True:
        candidate = f"{stem}_{suffix}.pdf"
        if not (target_dir / candidate).exists():
            return candidate
        suffix += 1


def _validate_pdf(path: Path) -> None:
    try:
        with path.open("rb") as handle:
            header = handle.read(5)
    except OSError as exc:
        raise PdfConversionError(f"Could not read generated PDF: {exc}") from exc

    if header != b"%PDF-":
        raise PdfConversionError("Converted file is not a valid PDF.")
    if path.stat().st_size < 100:
        raise PdfConversionError("Converted PDF appears to be empty or corrupt.")
