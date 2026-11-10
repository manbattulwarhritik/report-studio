"""Validation helpers for Data Entry records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CATEGORIES = ("Electronics", "Accessories", "Furniture")


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of a validation check."""

    ok: bool
    message: str = ""


def validate_record(
    name: Any,
    category: Any,
    quantity: Any,
    amount: Any,
) -> ValidationResult:
    """
    Validate Data Entry fields.

    Rules:
    - Name is required (non-empty after strip)
    - Category must be one of the known options
    - Quantity must be a positive integer
    - Amount must be a positive number
    """
    cleaned_name = str(name or "").strip()
    if not cleaned_name:
        return ValidationResult(False, "Name is required.")

    cleaned_category = str(category or "").strip()
    if not cleaned_category:
        return ValidationResult(False, "Please select a category.")
    if cleaned_category not in CATEGORIES:
        return ValidationResult(
            False,
            f"Category must be one of: {', '.join(CATEGORIES)}.",
        )

    quantity_result = _validate_positive_integer(quantity, field_name="Quantity")
    if not quantity_result.ok:
        return quantity_result

    amount_result = _validate_positive_number(amount, field_name="Amount")
    if not amount_result.ok:
        return amount_result

    return ValidationResult(True, "Valid")


def _validate_positive_integer(value: Any, field_name: str) -> ValidationResult:
    if isinstance(value, bool):
        return ValidationResult(False, f"{field_name} must be a positive integer.")

    if isinstance(value, int):
        number = value
    elif isinstance(value, float):
        if not value.is_integer():
            return ValidationResult(False, f"{field_name} must be a whole number.")
        number = int(value)
    elif isinstance(value, str):
        cleaned = value.strip()
        if not cleaned or not cleaned.isdigit():
            return ValidationResult(False, f"{field_name} must be a positive integer.")
        number = int(cleaned)
    else:
        return ValidationResult(False, f"{field_name} must be a positive integer.")

    if number <= 0:
        return ValidationResult(False, f"{field_name} must be greater than zero.")
    return ValidationResult(True)


def _validate_positive_number(value: Any, field_name: str) -> ValidationResult:
    if isinstance(value, bool):
        return ValidationResult(False, f"{field_name} must be a positive number.")

    try:
        if isinstance(value, str):
            cleaned = value.strip().replace(",", "")
            if not cleaned:
                return ValidationResult(False, f"{field_name} is required.")
            number = float(cleaned)
        else:
            number = float(value)
    except (TypeError, ValueError):
        return ValidationResult(False, f"{field_name} must be a positive number.")

    if number <= 0:
        return ValidationResult(False, f"{field_name} must be greater than zero.")
    return ValidationResult(True)
