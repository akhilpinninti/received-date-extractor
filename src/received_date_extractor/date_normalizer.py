
"""Normalize and validate detected manuscript dates."""

from __future__ import annotations

import re
from calendar import month_name, month_abbr
from datetime import date
from typing import Any


MONTHS = {}

for month_number in range(1, 13):
    MONTHS[month_name[month_number].lower()] = month_number
    MONTHS[month_abbr[month_number].lower()] = month_number

MONTHS["sept"] = 9


def _result(
    raw_date: str,
    normalized_date: str | None = None,
    status: str = "invalid",
    error: str | None = None,
    date_order_used: str | None = None,
) -> dict[str, Any]:
    return {
        "raw_date": raw_date,
        "normalized_date": normalized_date,
        "is_valid": status == "valid",
        "status": status,
        "error": error,
        "date_order_used": date_order_used,
    }


def _build_date(
    raw_date: str,
    year: int,
    month: int,
    day: int,
    date_order_used: str | None = None,
) -> dict[str, Any]:
    try:
        parsed = date(year, month, day)
    except ValueError as exc:
        return _result(
            raw_date,
            status="invalid",
            error=str(exc),
            date_order_used=date_order_used,
        )

    return _result(
        raw_date,
        normalized_date=parsed.isoformat(),
        status="valid",
        date_order_used=date_order_used,
    )


def _normalize_numeric(
    raw_date: str,
    date_order: str | None,
) -> dict[str, Any]:
    parts = re.split(r"[-/.]", raw_date)

    if len(parts) != 3:
        return _result(raw_date, error="Unsupported numeric date format.")

    try:
        first, second, third = map(int, parts)
    except ValueError:
        return _result(raw_date, error="Date contains non-numeric components.")

    # ISO format: YYYY-MM-DD
    if len(parts[0]) == 4:
        return _build_date(
            raw_date,
            year=first,
            month=second,
            day=third,
            date_order_used="YMD",
        )

    # This application currently supports four-digit years only.
    if len(parts[2]) != 4:
        return _result(
            raw_date,
            error="Numeric dates must contain a four-digit year.",
        )

    year = third

    if date_order is not None:
        if date_order not in {"DMY", "MDY"}:
            raise ValueError("date_order must be 'DMY', 'MDY', or None.")

        if date_order == "DMY":
            day, month = first, second
        else:
            month, day = first, second

        return _build_date(
            raw_date,
            year,
            month,
            day,
            date_order_used=date_order,
        )

    # Infer the order when one component cannot be a month.
    if first > 12 and second <= 12:
        return _build_date(
            raw_date,
            year,
            second,
            first,
            date_order_used="DMY",
        )

    if second > 12 and first <= 12:
        return _build_date(
            raw_date,
            year,
            first,
            second,
            date_order_used="MDY",
        )

    # Both interpretations produce the same date.
    if first == second:
        return _build_date(
            raw_date,
            year,
            first,
            second,
            date_order_used="DMY/MDY",
        )

    # Both values could represent months. Do not guess.
    if 1 <= first <= 12 and 1 <= second <= 12:
        return _result(
            raw_date,
            status="ambiguous",
            error="Numeric date is ambiguous between DMY and MDY.",
        )

    return _result(
        raw_date,
        error="Numeric date contains an invalid month or day.",
    )


def _normalize_named(raw_date: str) -> dict[str, Any]:
    cleaned = re.sub(r"(?<=\d)(?:st|nd|rd|th)\b", "", raw_date, flags=re.I)
    cleaned = cleaned.replace(",", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(".")

    # Day Month Year: 12 January 2025
    day_first = re.fullmatch(
        r"(\d{1,2})\s+([A-Za-z]+)\.?\s+(\d{4})",
        cleaned,
        flags=re.IGNORECASE,
    )

    if day_first:
        day = int(day_first.group(1))
        month_text = day_first.group(2).lower()
        year = int(day_first.group(3))

    else:
        # Month Day Year: January 12 2025
        month_first = re.fullmatch(
            r"([A-Za-z]+)\.?\s+(\d{1,2})\s+(\d{4})",
            cleaned,
            flags=re.IGNORECASE,
        )

        if not month_first:
            return _result(
                raw_date,
                error="Unsupported date format.",
            )

        month_text = month_first.group(1).lower()
        day = int(month_first.group(2))
        year = int(month_first.group(3))

    month = MONTHS.get(month_text)

    if month is None:
        return _result(
            raw_date,
            error=f"Unrecognized month name: {month_text}.",
        )

    return _build_date(
        raw_date,
        year,
        month,
        day,
        date_order_used="NAMED_MONTH",
    )


def normalize_date(
    raw_date: str,
    date_order: str | None = None,
) -> dict[str, Any]:
    """
    Validate and normalize a date string.

    Args:
        raw_date: Original date expression.
        date_order: Optional numeric convention, DMY or MDY.
                    None means ambiguous numeric dates remain unresolved.

    Returns:
        Dictionary containing normalized date and validation status.
    """
    if not isinstance(raw_date, str) or not raw_date.strip():
        return _result(
            str(raw_date),
            error="Date input must be a non-empty string.",
        )

    raw_date = raw_date.strip()

    if date_order is not None:
        date_order = date_order.upper()

        if date_order not in {"DMY", "MDY"}:
            raise ValueError("date_order must be 'DMY', 'MDY', or None.")

    # Numeric dates
    if re.fullmatch(
        r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}",
        raw_date,
    ) or re.fullmatch(
        r"\d{1,2}[-/.]\d{1,2}[-/.]\d{4}",
        raw_date,
    ):
        return _normalize_numeric(raw_date, date_order)

    # Named month dates
    return _normalize_named(raw_date)


def normalize_dates(
    candidates: list[dict[str, Any]],
    date_order: str | None = None,
) -> list[dict[str, Any]]:
    """Normalize detected date candidates while preserving their metadata."""
    results = []

    for candidate in candidates:
        raw_date = candidate.get("raw_date", "")

        normalized = normalize_date(
            raw_date,
            date_order=date_order,
        )

        results.append({
            **candidate,
            **normalized,
        })

    return results
