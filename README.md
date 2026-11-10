# Report Studio

Python + PyQt6 desktop application for generating Excel reports and converting them to PDF.

## Demo

Watch the walkthrough: [Demo video (Google Drive)](https://drive.google.com/file/d/1NWpyDS81mEN8h-DJ1nYCuRxHVzOnDkQJ/view?usp=drive_link)

## Setup

```bash
cd python-pyqt-report
source .venv/bin/activate
pip install -r requirements.txt
```

LibreOffice is required for Excel → PDF conversion (`soffice` on PATH, or Homebrew at `/opt/homebrew/bin/soffice`).

## Run

```bash
python app/main.py
```

or:

```bash
python -m app.main
```

## Tests

```bash
pytest
```

## Features

- **Dashboard** — Excel/PDF counts and recent activity
- **Data Entry** — editable records, validation, live totals
- **Excel generation** — branded OpenPyXL workbooks (`output/excel/`)
- **Excel Reports** — search, preview, download, delete
- **Convert to PDF** — LibreOffice headless conversion with page size/orientation
- **PDF Reports** — preview, print, download, delete
- **History** — local JSON activity log (`logs/history.json`)

## Storage

| Path | Purpose |
|---|---|
| `output/excel/` | Generated workbooks |
| `output/pdf/` | Converted PDFs |
| `logs/excel_catalog.json` | Excel library metadata |
| `logs/pdf_catalog.json` | PDF library metadata |
| `logs/history.json` | Activity history |

## Current milestone

