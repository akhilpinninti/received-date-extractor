
import pytest

from received_date_extractor.date_normalizer import (
    normalize_date,
    normalize_dates,
)


def test_normalize_day_month_year():
    result = normalize_date("12 January 2025")

    assert result["is_valid"] is True
    assert result["normalized_date"] == "2025-01-12"


def test_normalize_month_day_year():
    result = normalize_date("January 12, 2025")

    assert result["normalized_date"] == "2025-01-12"


def test_normalize_ordinal_date():
    result = normalize_date("2nd January 2025")

    assert result["normalized_date"] == "2025-01-02"


def test_normalize_abbreviated_month():
    result = normalize_date("12 Jan 2025")

    assert result["normalized_date"] == "2025-01-12"


def test_normalize_iso_date():
    result = normalize_date("2025-01-12")

    assert result["normalized_date"] == "2025-01-12"
    assert result["date_order_used"] == "YMD"


def test_normalize_unambiguous_dmy():
    result = normalize_date("13/04/2025")

    assert result["normalized_date"] == "2025-04-13"
    assert result["date_order_used"] == "DMY"


def test_normalize_unambiguous_mdy():
    result = normalize_date("04/13/2025")

    assert result["normalized_date"] == "2025-04-13"
    assert result["date_order_used"] == "MDY"


def test_ambiguous_numeric_date():
    result = normalize_date("03/04/2025")

    assert result["status"] == "ambiguous"
    assert result["normalized_date"] is None
    assert result["is_valid"] is False


def test_resolve_ambiguous_dmy():
    result = normalize_date("03/04/2025", date_order="DMY")

    assert result["normalized_date"] == "2025-04-03"


def test_resolve_ambiguous_mdy():
    result = normalize_date("03/04/2025", date_order="MDY")

    assert result["normalized_date"] == "2025-03-04"


def test_invalid_calendar_date():
    result = normalize_date("31/04/2025")

    assert result["is_valid"] is False
    assert result["status"] == "invalid"


def test_invalid_leap_year_date():
    result = normalize_date("29 February 2025")

    assert result["is_valid"] is False


def test_valid_leap_year_date():
    result = normalize_date("29 February 2024")

    assert result["normalized_date"] == "2024-02-29"


def test_invalid_month():
    result = normalize_date("12/13/2025", date_order="DMY")

    assert result["is_valid"] is False


def test_empty_input():
    result = normalize_date("")

    assert result["is_valid"] is False


def test_invalid_date_order():
    with pytest.raises(ValueError):
        normalize_date("12/01/2025", date_order="YMD")


def test_normalize_multiple_candidates():
    candidates = [
        {
            "raw_date": "12 January 2025",
            "context_type": "received",
            "location": "body",
        },
        {
            "raw_date": "20 March 2025",
            "context_type": "accepted",
            "location": "header",
        },
    ]

    results = normalize_dates(candidates)

    assert len(results) == 2
    assert results[0]["normalized_date"] == "2025-01-12"
    assert results[1]["normalized_date"] == "2025-03-20"

    # Original metadata must be preserved.
    assert results[0]["context_type"] == "received"
    assert results[1]["location"] == "header"
