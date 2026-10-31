
"""Detect potential date expressions in manuscript text."""

from __future__ import annotations

import re
from typing import Any


MONTH_NAMES = (
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)

ORDINAL = r"(?:st|nd|rd|th)?"

DATE_PATTERNS = [
    # ISO format: 2025-01-12 or 2025/01/12
    re.compile(r"(?<!\d)\d{4}[-/.]\d{1,2}[-/.]\d{1,2}(?!\d)"),

    # Numeric formats with four-digit or two-digit years
    re.compile(
        r"(?<!\d)\d{1,2}[-/.]\d{1,2}[-/.](?:\d{4}|\d{2})(?!\d)"
    ),

    # Month first: January 12, 2025 or Jan 12th 2025
    re.compile(
        rf"\b(?:{MONTH_NAMES})\.?\s+"
        rf"\d{{1,2}}{ORDINAL},?\s+\d{{4}}\b",
        re.IGNORECASE,
    ),

    # Day first: 12 January 2025 or 12th Jan, 2025
    re.compile(
        rf"\b\d{{1,2}}{ORDINAL}\s+"
        rf"(?:{MONTH_NAMES})\.?,?\s+\d{{4}}\b",
        re.IGNORECASE,
    ),
]

# Event labels must occur at the beginning of the local text segment.
# This prevents ordinary prose such as "samples were received on..."
# from being classified as the manuscript's received date.
EVENT_LABEL_PATTERN = re.compile(
    r"^\s*"
    r"(?:(?:article|manuscript)\s+history\s*[:\-]\s*)?"
    r"(?:(?:article|manuscript)\s+)?"
    r"(?P<keyword>"
    r"date\s+received|received|"
    r"revision\s+received|revised|"
    r"accepted|acceptance|"
    r"published|publication|"
    r"submitted|submission"
    r")\b",
    re.IGNORECASE,
)

CONTEXT_WINDOW = 100

# Punctuation and newlines separate local event labels.
SEGMENT_BOUNDARIES = re.compile(r"[\n\r.!?;]+")


def _get_local_segment(text: str, start: int, end: int) -> str:
    """Return the sentence-like segment containing a date."""
    previous_boundaries = list(
        SEGMENT_BOUNDARIES.finditer(text, 0, start)
    )

    segment_start = (
        previous_boundaries[-1].end()
        if previous_boundaries
        else 0
    )

    next_boundary = SEGMENT_BOUNDARIES.search(text, end)
    segment_end = (
        next_boundary.start()
        if next_boundary
        else len(text)
    )

    return text[segment_start:segment_end].strip()


def _classify_context(
    text: str,
    start: int,
    end: int,
) -> tuple[str, str | None]:
    """Classify a date only when an explicit event label precedes it."""
    segment = _get_local_segment(text, start, end)

    match = EVENT_LABEL_PATTERN.match(segment)

    if not match:
        return "unknown", None

    keyword = match.group("keyword").lower()

    if keyword in ("received", "date received"):
        category = "received"
    elif keyword in ("revision received", "revised"):
        category = "revised"
    elif keyword in ("accepted", "acceptance"):
        category = "accepted"
    elif keyword in ("published", "publication"):
        category = "published"
    else:
        category = "submitted"

    return category, keyword


def detect_dates(
    text: str,
    metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Detect potential date expressions in text.

    Detection does not validate calendar dates or resolve
    ambiguous numeric date formats.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    candidates = []

    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            start, end = match.span()

            context_type, keyword = _classify_context(
                text,
                start,
                end,
            )

            context_start = max(0, start - CONTEXT_WINDOW)
            context_end = min(len(text), end + CONTEXT_WINDOW)

            candidate = {
                "raw_date": match.group(0),
                "matched_text": match.group(0),
                "start": start,
                "end": end,
                "context": text[context_start:context_end].strip(),
                "context_type": context_type,
                "context_keyword": keyword,
            }

            if metadata:
                candidate.update(metadata)

            candidates.append(candidate)

    # Remove duplicate matches while preserving their positions.
    unique_candidates = {}

    for candidate in candidates:
        key = (
            candidate["start"],
            candidate["end"],
            candidate["raw_date"],
        )
        unique_candidates[key] = candidate

    return sorted(
        unique_candidates.values(),
        key=lambda item: item["start"],
    )


def detect_dates_in_blocks(
    blocks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Detect dates across extracted manuscript text blocks."""
    all_candidates = []

    for block_index, block in enumerate(blocks):
        text = block.get("text", "")

        if not isinstance(text, str):
            continue

        metadata = {
            key: value
            for key, value in block.items()
            if key != "text"
        }

        metadata.setdefault("block_index", block_index)

        candidates = detect_dates(text, metadata)
        all_candidates.extend(candidates)

    return all_candidates
