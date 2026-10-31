
"""Generate structured CSV reports for manuscript received dates."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


CSV_COLUMNS = [
    "filename",
    "status",
    "received_date",
    "confidence",
    "requires_manual_review",
    "reason",
    "candidate_count",
    "received_candidate_count",
    "raw_received_dates",
    "source_locations",
]


def _prepare_row(result: dict[str, Any]) -> dict[str, Any]:
    """Convert a processing result into a flat CSV row."""

    decision = result.get("decision", result)

    selected_candidate = decision.get("selected_candidate") or {}

    candidates = result.get("candidates", [])

    received_candidates = [
        candidate
        for candidate in candidates
        if candidate.get("context_type") == "received"
    ]

    raw_dates = [
        candidate.get("raw_date", "")
        for candidate in received_candidates
    ]

    locations = [
        candidate.get("location", "unknown")
        for candidate in received_candidates
    ]

    # Support results where candidate counts are supplied directly
    # by the decision engine.
    candidate_count = decision.get(
        "candidate_count",
        len(candidates),
    )

    received_candidate_count = decision.get(
        "received_candidate_count",
        len(received_candidates),
    )

    return {
        "filename": result.get("filename", ""),
        "status": decision.get("status", "UNKNOWN"),
        "received_date": decision.get("selected_date") or "",
        "confidence": decision.get("confidence", 0.0),
        "requires_manual_review": decision.get(
            "requires_manual_review",
            True,
        ),
        "reason": decision.get("reason", ""),
        "candidate_count": candidate_count,
        "received_candidate_count": received_candidate_count,
        "raw_received_dates": " | ".join(raw_dates),
        "source_locations": " | ".join(locations),
    }


def generate_csv(
    results: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """
    Generate a CSV report from manuscript processing results.

    Args:
        results: List of manuscript processing result dictionaries.
        output_path: Destination CSV file path.

    Returns:
        Path to the generated CSV file.
    """
    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        mode="w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_COLUMNS,
            extrasaction="ignore",
        )

        writer.writeheader()

        for result in results:
            writer.writerow(_prepare_row(result))

    return output_file
