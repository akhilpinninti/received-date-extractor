
from received_date_extractor.decision_engine import select_received_date


def make_candidate(
    raw_date,
    normalized_date,
    context_type="received",
    status="valid",
    location="body",
    block_index=0,
):
    return {
        "raw_date": raw_date,
        "normalized_date": normalized_date,
        "context_type": context_type,
        "status": status,
        "is_valid": status == "valid",
        "location": location,
        "block_index": block_index,
    }


def test_select_single_received_date():
    candidates = [
        make_candidate("12 January 2025", "2025-01-12")
    ]

    result = select_received_date(candidates)

    assert result["status"] == "SUCCESS"
    assert result["selected_date"] == "2025-01-12"
    assert result["requires_manual_review"] is False


def test_ignore_revised_accepted_and_published_dates():
    candidates = [
        make_candidate(
            "12 January 2025",
            "2025-01-12",
            context_type="received",
        ),
        make_candidate(
            "20 February 2025",
            "2025-02-20",
            context_type="revised",
        ),
        make_candidate(
            "5 March 2025",
            "2025-03-05",
            context_type="accepted",
        ),
        make_candidate(
            "15 March 2025",
            "2025-03-15",
            context_type="published",
        ),
    ]

    result = select_received_date(candidates)

    assert result["selected_date"] == "2025-01-12"


def test_no_received_date():
    candidates = [
        make_candidate(
            "20 February 2025",
            "2025-02-20",
            context_type="revised",
        )
    ]

    result = select_received_date(candidates)

    assert result["status"] == "NOT_FOUND"
    assert result["selected_date"] is None
    assert result["requires_manual_review"] is True


def test_no_candidates():
    result = select_received_date([])

    assert result["status"] == "NOT_FOUND"
    assert result["selected_date"] is None


def test_conflicting_received_dates_require_review():
    candidates = [
        make_candidate(
            "12 January 2025",
            "2025-01-12",
            block_index=0,
        ),
        make_candidate(
            "15 January 2025",
            "2025-01-15",
            block_index=1,
        ),
    ]

    result = select_received_date(candidates)

    assert result["status"] == "REVIEW_REQUIRED"
    assert result["selected_date"] is None
    assert result["requires_manual_review"] is True


def test_duplicate_received_dates_are_grouped():
    candidates = [
        make_candidate(
            "12 January 2025",
            "2025-01-12",
            location="body",
            block_index=0,
        ),
        make_candidate(
            "January 12, 2025",
            "2025-01-12",
            location="header",
            block_index=1,
        ),
    ]

    result = select_received_date(candidates)

    assert result["status"] == "SUCCESS"
    assert result["selected_date"] == "2025-01-12"
    assert result["requires_manual_review"] is False


def test_ambiguous_received_date_requires_review():
    candidates = [
        make_candidate(
            "03/04/2025",
            None,
            status="ambiguous",
        )
    ]

    result = select_received_date(candidates)

    assert result["status"] == "REVIEW_REQUIRED"
    assert result["selected_date"] is None


def test_invalid_received_date_requires_review():
    candidates = [
        make_candidate(
            "31/04/2025",
            None,
            status="invalid",
        )
    ]

    result = select_received_date(candidates)

    assert result["status"] == "REVIEW_REQUIRED"
    assert result["selected_date"] is None


def test_unknown_context_is_not_selected():
    candidates = [
        make_candidate(
            "12 January 2025",
            "2025-01-12",
            context_type="unknown",
        )
    ]

    result = select_received_date(candidates)

    assert result["status"] == "NOT_FOUND"
    assert result["selected_date"] is None


def test_body_candidate_has_higher_location_score():
    candidates = [
        make_candidate(
            "12 January 2025",
            "2025-01-12",
            location="footer",
        ),
        make_candidate(
            "12 January 2025",
            "2025-01-12",
            location="body",
        ),
    ]

    result = select_received_date(candidates)

    assert result["status"] == "SUCCESS"
    assert result["selected_candidate"]["location"] == "body"


def test_valid_and_ambiguous_received_dates_require_review():
    candidates = [
        make_candidate(
            "12 January 2025",
            "2025-01-12",
        ),
        make_candidate(
            "03/04/2025",
            None,
            status="ambiguous",
        ),
    ]

    result = select_received_date(candidates)

    assert result["status"] == "REVIEW_REQUIRED"
    assert result["selected_date"] is None


def test_confidence_is_bounded():
    candidates = [
        make_candidate(
            "12 January 2025",
            "2025-01-12",
            location="body",
        )
    ]

    result = select_received_date(candidates)

    assert 0.0 <= result["confidence"] <= 1.0


def test_result_contains_audit_information():
    candidates = [
        make_candidate(
            "12 January 2025",
            "2025-01-12",
        ),
        make_candidate(
            "20 February 2025",
            "2025-02-20",
            context_type="revised",
        ),
    ]

    result = select_received_date(candidates)

    assert result["candidate_count"] == 2
    assert result["received_candidate_count"] == 1
    assert result["reason"]
    assert result["selected_candidate"]["raw_date"] == "12 January 2025"
