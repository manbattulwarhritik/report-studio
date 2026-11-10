"""Local JSON activity history for Report Studio."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.utils.paths import history_path


@dataclass
class HistoryEntry:
    """One recorded application action."""

    id: str
    timestamp: str
    activity: str
    details: str
    status: str
    kind: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HistoryEntry:
        return cls(
            id=str(data["id"]),
            timestamp=str(data["timestamp"]),
            activity=str(data["activity"]),
            details=str(data.get("details", "")),
            status=str(data.get("status", "Success")),
            kind=str(data.get("kind", "info")),
        )


class HistoryService:
    """Append-only activity log stored as JSON."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path else history_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def add(
        self,
        activity: str,
        details: str,
        *,
        status: str = "Success",
        kind: str = "info",
    ) -> HistoryEntry:
        entry = HistoryEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(timespec="seconds"),
            activity=activity,
            details=details,
            status=status,
            kind=kind,
        )
        entries = self._read()
        entries.append(entry)
        self._write(entries)
        return entry

    def list_entries(self, limit: int | None = None) -> list[HistoryEntry]:
        # Append-only storage: reverse for newest-first, including same-second events.
        entries = list(reversed(self._read()))
        if limit is not None:
            return entries[: max(0, limit)]
        return entries

    def clear(self) -> None:
        self._write([])

    def _read(self) -> list[HistoryEntry]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(raw, list):
            return []

        entries: list[HistoryEntry] = []
        for item in raw:
            if isinstance(item, dict):
                try:
                    entries.append(HistoryEntry.from_dict(item))
                except (KeyError, TypeError, ValueError):
                    continue
        return entries

    def _write(self, entries: list[HistoryEntry]) -> None:
        payload = [entry.to_dict() for entry in entries]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
