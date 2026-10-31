
from received_date_extractor.date_detector import (
    detect_dates,
    detect_dates_in_blocks,
)


def test_detect_day_month_year():
    results = detect_dates("Received on 12 January 2025.")
    assert len(results) == 1
    assert results[0]["raw_date"] == "12 January 2025"
    assert results[0]["context_type"] == "received"


def test_detect_month_day_year():
    results = detect_dates("Manuscript accepted on January 12, 2025.")
    assert len(results) == 1
    assert results[0]["raw_date"] == "January 12, 2025"
    assert results[0]["context_type"] == "accepted"


def test_detect_numeric_date():
    results = detect_dates("Received: 12/01/2025.")
    assert len(results) == 1
    assert results[0]["raw_date"] == "12/01/2025"
    assert results[0]["context_type"] == "received"


def test_detect_iso_date():
    results = detect_dates("Received: 2025-01-12.")
    assert len(results) == 1
    assert results[0]["raw_date"] == "2025-01-12"


def test_detect_multiple_dates():
    results = detect_dates(
        "Received 12 January 2025. "
        "Revised 20 February 2025. "
        "Accepted 5 March 2025."
    )
    assert len(results) == 3
    assert [
        result["context_type"] for result in results
    ] == ["received", "revised", "accepted"]


def test_detect_ordinal_date():
    results = detect_dates("Received on 2nd January 2025.")
    assert len(results) == 1
    assert results[0]["raw_date"] == "2nd January 2025"


def test_no_dates():
    assert detect_dates(
        "This manuscript contains no date information."
    ) == []


def test_empty_text():
    assert detect_dates("") == []
    assert detect_dates("   ") == []


def test_unknown_date_context():
    results = detect_dates(
        "The experiment was conducted on 12 January 2025."
    )
    assert len(results) == 1
    assert results[0]["context_type"] == "unknown"


def test_detect_dates_in_blocks():
    blocks = [
        {
            "text": "Received on 12 January 2025.",
            "location": "paragraph",
            "paragraph_index": 0,
        },
        {
            "text": "Accepted on 20 March 2025.",
            "location": "header",
            "section_index": 0,
        },
    ]

    results = detect_dates_in_blocks(blocks)
    assert len(results) == 2
    assert results[0]["location"] == "paragraph"
    assert results[1]["location"] == "header"
    assert results[0]["block_index"] == 0
    assert results[1]["block_index"] == 1


def test_ordinary_prose_received_is_not_manuscript_received():
    results = detect_dates(
        "The authors received samples on 5 May 2025."
    )
    assert len(results) == 1
    assert results[0]["context_type"] == "unknown"


def test_files_received_is_not_manuscript_received():
    results = detect_dates(
        "The files were received on 14 February 2025."
    )
    assert len(results) == 1
    assert results[0]["context_type"] == "unknown"


def test_detect_two_digit_year_received_date():
    results = detect_dates("Received: 12/05/26.")
    assert len(results) == 1
    assert results[0]["raw_date"] == "12/05/26"
    assert results[0]["context_type"] == "received"
