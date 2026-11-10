"""Unit tests for Data Entry validation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.validation_service import CATEGORIES, validate_record


def test_valid_record_passes() -> None:
    result = validate_record("Laptop", "Electronics", 2, 90000)
    assert result.ok
    assert result.message == "Valid"


def test_valid_record_accepts_string_quantity_and_comma_amount() -> None:
    result = validate_record("Chair", "Furniture", "3", "1,250.50")
    assert result.ok


def test_valid_record_accepts_whole_float_quantity() -> None:
    result = validate_record("Desk", "Furniture", 2.0, 500)
    assert result.ok


@pytest.mark.parametrize(
    ("name", "category", "quantity", "amount", "expected"),
    [
        ("", "Electronics", 1, 100, "Name is required."),
        ("   ", "Electronics", 1, 100, "Name is required."),
        ("Mouse", "", 1, 100, "Please select a category."),
        ("Mouse", "Unknown", 1, 100, "Category must be one of"),
        ("Mouse", "Accessories", 0, 100, "Quantity must be greater than zero."),
        ("Mouse", "Accessories", -2, 100, "Quantity must be greater than zero."),
        ("Mouse", "Accessories", 1.5, 100, "Quantity must be a whole number."),
        ("Mouse", "Accessories", "abc", 100, "Quantity must be a positive integer."),
        ("Mouse", "Accessories", True, 100, "Quantity must be a positive integer."),
        ("Mouse", "Accessories", 1, 0, "Amount must be greater than zero."),
        ("Mouse", "Accessories", 1, -10, "Amount must be greater than zero."),
        ("Mouse", "Accessories", 1, "not-a-number", "Amount must be a positive number."),
        ("Mouse", "Accessories", 1, "", "Amount is required."),
        ("Mouse", "Accessories", 1, False, "Amount must be a positive number."),
    ],
)
def test_invalid_records(name, category, quantity, amount, expected) -> None:
    result = validate_record(name, category, quantity, amount)
    assert not result.ok
    assert expected in result.message


def test_known_categories() -> None:
    assert CATEGORIES == ("Electronics", "Accessories", "Furniture")
