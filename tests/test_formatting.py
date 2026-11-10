"""Unit tests for INR display formatting."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.formatting import format_inr


def test_format_inr_basic_grouping() -> None:
    assert format_inr(90) == "₹90"
    assert format_inr(2500) == "₹2,500"
    assert format_inr(135000) == "₹1,35,000"


def test_format_inr_crore_scale() -> None:
    assert format_inr(12345678) == "₹1,23,45,678"


def test_format_inr_fraction_and_negative() -> None:
    assert format_inr(90.5) == "₹90.50"
    assert format_inr(-2500) == "-₹2,500"
    assert format_inr(-90.5) == "-₹90.50"
