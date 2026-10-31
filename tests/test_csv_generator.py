
import csv

from received_date_extractor.csv_generator import (
    CSV_COLUMNS,
    generate_csv,
)


def test_generate_csv_with_successful_result(tmp_path):
    output = tmp_path / "results.csv"

    results = [
        {
            "filename": "manuscript1.docx",
            "decision": {
                "status": "SUCCESS",
                "selected_date": "2025-01-12",
                "confidence": 0.91,
                "requires_manual_review": False,
                "reason": "Received date identified.",
                "candidate_count": 3,
                "received_candidate_count": 1,
                "selected_candidate": {
                    "raw_date": "12 January 2025",
                    "location": "body",
                },
            },
            "candidates": [
                {
                    "raw_date": "12 January 2025",
                    "context_type": "received",
                    "location": "body",
                }
            ],
        }
    ]

    result_path = generate_csv(results, output)

    assert result_path.exists()

    with result_path.open(
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["filename"] == "manuscript1.docx"
    assert rows[0]["received_date"] == "2025-01-12"
    assert rows[0]["status"] == "SUCCESS"
    assert rows[0]["requires_manual_review"] == "False"


def test_generate_csv_with_multiple_manuscripts(tmp_path):
    output = tmp_path / "results.csv"

    results = [
        {
            "filename": "first.docx",
            "decision": {
                "status": "SUCCESS",
                "selected_date": "2025-01-12",
                "confidence": 0.91,
                "requires_manual_review": False,
            },
        },
        {
            "filename": "second.docx",
            "decision": {
                "status": "NOT_FOUND",
                "selected_date": None,
                "confidence": 0.0,
                "requires_manual_review": True,
            },
        },
    ]

    generate_csv(results, output)

    with output.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["received_date"] == "2025-01-12"
    assert rows[1]["received_date"] == ""
    assert rows[1]["status"] == "NOT_FOUND"


def test_generate_empty_csv(tmp_path):
    output = tmp_path / "empty.csv"

    generate_csv([], output)

    with output.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file))

    assert len(rows) == 1
    assert rows[0] == CSV_COLUMNS


def test_create_output_directory(tmp_path):
    output = tmp_path / "reports" / "nested" / "results.csv"

    generate_csv([], output)

    assert output.exists()


def test_csv_contains_all_expected_columns(tmp_path):
    output = tmp_path / "results.csv"

    generate_csv([], output)

    with output.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        assert reader.fieldnames == CSV_COLUMNS


def test_export_received_date_candidates(tmp_path):
    output = tmp_path / "results.csv"

    results = [
        {
            "filename": "manuscript.docx",
            "decision": {
                "status": "SUCCESS",
                "selected_date": "2025-01-12",
                "confidence": 0.91,
                "requires_manual_review": False,
                "candidate_count": 3,
                "received_candidate_count": 1,
            },
            "candidates": [
                {
                    "raw_date": "12 January 2025",
                    "context_type": "received",
                    "location": "body",
                },
                {
                    "raw_date": "20 February 2025",
                    "context_type": "revised",
                    "location": "body",
                },
            ],
        }
    ]

    generate_csv(results, output)

    with output.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["raw_received_dates"] == "12 January 2025"
    assert rows[0]["source_locations"] == "body"


def test_flat_decision_result_is_supported(tmp_path):
    output = tmp_path / "results.csv"

    results = [
        {
            "filename": "manuscript.docx",
            "status": "SUCCESS",
            "selected_date": "2025-01-12",
            "confidence": 0.91,
            "requires_manual_review": False,
        }
    ]

    generate_csv(results, output)

    with output.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["received_date"] == "2025-01-12"


def test_csv_preserves_unicode_filename(tmp_path):
    output = tmp_path / "results.csv"

    results = [
        {
            "filename": "manuscript_é.docx",
            "decision": {
                "status": "SUCCESS",
                "selected_date": "2025-01-12",
            },
        }
    ]

    generate_csv(results, output)

    with output.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["filename"] == "manuscript_é.docx"
