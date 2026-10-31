
"""Select the most likely received date from normalized candidates."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


CONTEXT_SCORES = {
    "received": 100,
    "revised": 0,
    "accepted": 0,
    "published": 0,
    "submitted": 0,
    "unknown": 0,
}

LOCATION_SCORES = {
    "body": 10,
    "paragraph": 10,
    "body_table": 8,
    "table": 8,
    "header": 5,
    "header_table": 5,
    "footer": 3,
    "footer_table": 3,
}


def _location_score(candidate: dict[str, Any]) -> int:
    location = str(candidate.get("location", "")).lower()
    return LOCATION_SCORES.get(location, 0)


def _is_valid_received_candidate(
    candidate: dict[str, Any],
) -> bool:
    return (
        candidate.get("context_type") == "received"
        and candidate.get("status") == "valid"
        and bool(candidate.get("normalized_date"))
    )


def _candidate_score(candidate: dict[str, Any]) -> int:
    """Calculate a transparent ranking score for a candidate."""
    context = candidate.get("context_type", "unknown")
    context_score = CONTEXT_SCORES.get(context, 0)

    return context_score + _location_score(candidate)


def _review_result(
    status: str,
    reason: str,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "status": status,
        "selected_date": None,
        "selected_candidate": None,
        "confidence": 0.0,
        "requires_manual_review": True,
        "reason": reason,
        "candidate_count": len(candidates),
        "received_candidate_count": sum(
            candidate.get("context_type") == "received"
            for candidate in candidates
        ),
    }


def select_received_date(
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Select the received date from normalized date candidates.

    Selection rules:
    1. Only explicitly identified received-date candidates are eligible.
    2. Invalid and ambiguous dates cannot be selected.
    3. Repeated occurrences of the same normalized date are grouped.
    4. Conflicting valid received dates require manual review.
    5. Revised, accepted, published and unknown dates are never
       selected as received dates.
    """
    if not candidates:
        return _review_result(
            "NOT_FOUND",
            "No date candidates were detected.",
            candidates,
        )

    received_candidates = [
        candidate
        for candidate in candidates
        if candidate.get("context_type") == "received"
    ]

    if not received_candidates:
        return _review_result(
            "NOT_FOUND",
            "No explicitly identified received-date candidate was found.",
            candidates,
        )

    valid_candidates = [
        candidate
        for candidate in received_candidates
        if _is_valid_received_candidate(candidate)
    ]

    ambiguous_candidates = [
        candidate
        for candidate in received_candidates
        if candidate.get("status") == "ambiguous"
    ]

    if not valid_candidates:
        if ambiguous_candidates:
            return _review_result(
                "REVIEW_REQUIRED",
                "Received-date candidates exist, but their numeric formats "
                "are ambiguous.",
                candidates,
            )

        return _review_result(
            "REVIEW_REQUIRED",
            "Received-date candidates were found, but none is valid.",
            candidates,
        )

    # Group candidates by their normalized date.
    date_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for candidate in valid_candidates:
        date_groups[candidate["normalized_date"]].append(candidate)

    if len(date_groups) > 1:
        return _review_result(
            "REVIEW_REQUIRED",
            "Multiple conflicting valid received dates were found.",
            candidates,
        )

    selected_date = next(iter(date_groups))
    matching_candidates = date_groups[selected_date]

    # Select the strongest source occurrence for the same date.
    selected_candidate = max(
        matching_candidates,
        key=lambda candidate: (
            _candidate_score(candidate),
            -int(candidate.get("block_index", 0)),
        ),
    )

    # An unresolved ambiguous received date could conflict with
    # the otherwise valid selected date.
    if ambiguous_candidates:
        return _review_result(
            "REVIEW_REQUIRED",
            "A valid received date and an ambiguous received-date "
            "candidate coexist. Manual verification is required.",
            candidates,
        )

    score = _candidate_score(selected_candidate)

    # Confidence is a rule-based indicator, not a statistical probability.
    confidence = min(0.99, 0.80 + (score / 1000))

    return {
        "status": "SUCCESS",
        "selected_date": selected_date,
        "selected_candidate": selected_candidate,
        "confidence": round(confidence, 2),
        "requires_manual_review": False,
        "reason": (
            "A single valid received date was identified. "
            "Repeated occurrences agree."
        ),
        "candidate_count": len(candidates),
        "received_candidate_count": len(received_candidates),
    }
