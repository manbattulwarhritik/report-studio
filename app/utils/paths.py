"""Project path helpers."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the repository root (parent of the `app` package)."""
    return Path(__file__).resolve().parents[2]


def excel_output_dir() -> Path:
    path = project_root() / "output" / "excel"
    path.mkdir(parents=True, exist_ok=True)
    return path


def pdf_output_dir() -> Path:
    path = project_root() / "output" / "pdf"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    path = project_root() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def excel_catalog_path() -> Path:
    return logs_dir() / "excel_catalog.json"


def pdf_catalog_path() -> Path:
    return logs_dir() / "pdf_catalog.json"


def history_path() -> Path:
    return logs_dir() / "history.json"
