"""End-to-end received-date extraction pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from received_date_extractor.file_validator import validate_docx
from received_date_extractor.manuscript_inspector import inspect_manuscript
from received_date_extractor.date_detector import detect_dates_in_blocks
from received_date_extractor.date_normalizer import normalize_dates
from received_date_extractor.decision_engine import select_received_date
from received_date_extractor.csv_generator import generate_csv
from received_date_extractor.config import (
    DEFAULT_DATE_ORDER,
    RECURSIVE_SCAN,
)


def process_manuscript(
    file_path: str | Path,
    date_order: str | None = DEFAULT_DATE_ORDER,
) -> dict[str, Any]:
    """Process one manuscript and return its received-date result."""

    path = Path(file_path)
    validation = validate_docx(path)

    if not validation["is_valid"]:
        return {
            "filename": path.name,
            "file_path": str(path),
            "status": "INVALID_FILE",
            "selected_date": None,
            "confidence": 0.0,
            "requires_manual_review": True,
            "reason": "; ".join(validation["errors"]),
            "candidate_count": 0,
            "received_candidate_count": 0,
            "selected_candidate": None,
            "candidates": [],
        }

    try:
        inspection = inspect_manuscript(path)

        if inspection["status"] != "VALID":
            return {
                "filename": path.name,
                "file_path": str(path),
                "status": "INVALID_FILE",
                "selected_date": None,
                "confidence": 0.0,
                "requires_manual_review": True,
                "reason": inspection["error_message"] or "DOCX inspection failed.",
                "candidate_count": 0,
                "received_candidate_count": 0,
                "selected_candidate": None,
                "candidates": [],
            }

        detected_candidates = detect_dates_in_blocks(
            inspection["extracted_text"]
        )

        normalized_candidates = normalize_dates(
            detected_candidates,
            date_order=date_order,
        )

        decision = select_received_date(normalized_candidates)

        return {
            "filename": path.name,
            "file_path": str(path),
            "status": decision["status"],
            "selected_date": decision["selected_date"],
            "confidence": decision["confidence"],
            "requires_manual_review": decision["requires_manual_review"],
            "reason": decision["reason"],
            "candidate_count": decision["candidate_count"],
            "received_candidate_count": decision["received_candidate_count"],
            "selected_candidate": decision["selected_candidate"],
            "candidates": normalized_candidates,
            "extraction_metadata": {
                "paragraph_count": inspection["paragraph_count"],
                "table_count": inspection["table_count"],
                "header_count": inspection["header_count"],
                "footer_count": inspection["footer_count"],
                "extracted_text_length": inspection["extracted_text_length"],
                "special_xml_structures": inspection["special_xml_structures"],
            },
        }

    except Exception as exc:
        return {
            "filename": path.name,
            "file_path": str(path),
            "status": "PROCESSING_ERROR",
            "selected_date": None,
            "confidence": 0.0,
            "requires_manual_review": True,
            "reason": f"Processing failed: {exc}",
            "candidate_count": 0,
            "received_candidate_count": 0,
            "selected_candidate": None,
            "candidates": [],
        }


def process_directory(
    input_directory: str | Path,
    output_csv: str | Path,
    date_order: str | None = DEFAULT_DATE_ORDER,
    recursive: bool = RECURSIVE_SCAN,
) -> list[dict[str, Any]]:
    """Process DOCX manuscripts in a directory and export a CSV."""

    input_path = Path(input_directory)

    if not input_path.exists() or not input_path.is_dir():
        raise NotADirectoryError(
            f"Input directory does not exist: {input_path}"
        )

    pattern = "**/*.docx" if recursive else "*.docx"
    manuscript_paths = sorted(
        input_path.glob(pattern),
        key=lambda path: str(path).lower(),
    )

    results = [
        process_manuscript(path, date_order=date_order)
        for path in manuscript_paths
    ]

    generate_csv(results, output_csv)

    return results