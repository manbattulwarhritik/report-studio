"""Unit tests for project path helpers."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.paths import (
    excel_catalog_path,
    excel_output_dir,
    history_path,
    pdf_catalog_path,
    pdf_output_dir,
    project_root,
)


def test_project_root_points_at_repo() -> None:
    root = project_root()
    assert (root / "app").is_dir()
    assert (root / "tests").is_dir()


def test_output_and_log_paths_under_project() -> None:
    root = project_root()
    assert excel_output_dir() == root / "output" / "excel"
    assert pdf_output_dir() == root / "output" / "pdf"
    assert excel_catalog_path() == root / "logs" / "excel_catalog.json"
    assert pdf_catalog_path() == root / "logs" / "pdf_catalog.json"
    assert history_path() == root / "logs" / "history.json"
