"""Tests for activity history persistence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.history_service import HistoryService


def test_history_add_and_list(tmp_path: Path) -> None:
    service = HistoryService(path=tmp_path / "history.json")
    service.add("Excel report generated", "demo.xlsx", kind="excel_generated")
    service.add("PDF downloaded", "demo.pdf", kind="pdf_downloaded")

    entries = service.list_entries()
    assert len(entries) == 2
    assert entries[0].activity == "PDF downloaded"
    assert entries[1].details == "demo.xlsx"

    recent = service.list_entries(limit=1)
    assert len(recent) == 1
    assert recent[0].activity == "PDF downloaded"


def test_history_clear(tmp_path: Path) -> None:
    service = HistoryService(path=tmp_path / "history.json")
    service.add("Report deleted", "old.xlsx", status="Success", kind="excel_deleted")
    service.clear()
    assert service.list_entries() == []


def test_history_persists_status_and_kind(tmp_path: Path) -> None:
    service = HistoryService(path=tmp_path / "history.json")
    entry = service.add(
        "Conversion failed",
        "demo.xlsx",
        status="Failed",
        kind="pdf_failed",
    )
    assert entry.status == "Failed"
    assert entry.kind == "pdf_failed"

    reloaded = HistoryService(path=tmp_path / "history.json")
    listed = reloaded.list_entries()
    assert len(listed) == 1
    assert listed[0].status == "Failed"
    assert listed[0].kind == "pdf_failed"


def test_history_skips_corrupt_entries(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text(
        json.dumps(
            [
                {"broken": True},
                {
                    "id": "h-1",
                    "timestamp": "2026-11-10T21:00:00",
                    "activity": "Excel generated",
                    "details": "demo.xlsx",
                    "status": "Success",
                    "kind": "excel_generated",
                },
            ]
        ),
        encoding="utf-8",
    )
    service = HistoryService(path=path)
    entries = service.list_entries()
    assert len(entries) == 1
    assert entries[0].id == "h-1"


def test_history_handles_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text("{not-json", encoding="utf-8")
    service = HistoryService(path=path)
    assert service.list_entries() == []


def test_history_limit_zero_returns_empty(tmp_path: Path) -> None:
    service = HistoryService(path=tmp_path / "history.json")
    service.add("Excel report generated", "demo.xlsx")
    assert service.list_entries(limit=0) == []
