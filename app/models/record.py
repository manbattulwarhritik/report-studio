"""Data record used by Data Entry and later Excel generation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Record:
    """A single line item entered by the user."""

    name: str
    category: str
    quantity: int
    amount: float
