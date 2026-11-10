"""Display formatting helpers."""

from __future__ import annotations


def format_inr(amount: float | int) -> str:
    """
    Format a number using Indian grouping with a rupee symbol.

    Examples:
        135000 -> ₹1,35,000
        2500   -> ₹2,500
        90.5   -> ₹90.50
    """
    value = float(amount)
    negative = value < 0
    value = abs(value)

    has_fraction = abs(value - round(value)) > 1e-9
    if has_fraction:
        integer_part, fraction_part = f"{value:.2f}".split(".")
    else:
        integer_part = str(int(round(value)))
        fraction_part = None

    grouped = _group_indian(integer_part)
    formatted = f"₹{grouped}"
    if fraction_part is not None:
        formatted = f"{formatted}.{fraction_part}"
    if negative:
        formatted = f"-{formatted}"
    return formatted


def _group_indian(digits: str) -> str:
    """Apply Indian thousand/lakh/crore comma grouping to an integer digit string."""
    if len(digits) <= 3:
        return digits

    last_three = digits[-3:]
    remaining = digits[:-3]
    groups: list[str] = []

    while remaining:
        groups.append(remaining[-2:])
        remaining = remaining[:-2]

    groups.reverse()
    return ",".join(groups + [last_three])
