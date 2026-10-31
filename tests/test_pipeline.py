
from pathlib import Path

from docx import Document

from received_date_extractor.pipeline import (
    process_manuscript,
    process_directory,
)


def create_manuscript(path: Path, text: str):
    document = Document()
    document.add_paragraph(text)
    document.save(path)
    return path


def test_process_manuscript_with_received_date(tmp_path):
    path = create_manuscript(
        tmp_path / "paper.docx",
        "Manuscript received on 12 January 2025.",
    )

    result = process_manuscript(path)

    assert result["status"] == "SUCCESS"
    assert result["selected_date"] == "2025-01-12"
    assert result["requires_manual_review"] is False


def test_process_manuscript_without_received_date(tmp_path):
    path = create_manuscript(
        tmp_path / "paper.docx",
        "This manuscript was accepted on 12 January 2025.",
    )

    result = process_manuscript(path)

    assert result["status"] == "NOT_FOUND"
    assert result["selected_date"] is None


def test_process_manuscript_with_ambiguous_date(tmp_path):
    path = create_manuscript(
        tmp_path / "paper.docx",
        "Manuscript received on 03/04/2025.",
    )

    result = process_manuscript(path)

    assert result["status"] == "REVIEW_REQUIRED"
    assert result["requires_manual_review"] is True


def test_process_invalid_file(tmp_path):
    path = tmp_path / "broken.docx"
    path.write_text("not a valid Word document")

    result = process_manuscript(path)

    assert result["status"] == "INVALID_FILE"
    assert result["requires_manual_review"] is True


def test_process_directory_and_generate_csv(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    create_manuscript(
        input_dir / "paper1.docx",
        "Manuscript received on 12 January 2025.",
    )

    create_manuscript(
        input_dir / "paper2.docx",
        "Manuscript accepted on 15 March 2025.",
    )

    output_csv = tmp_path / "output" / "results.csv"

    results = process_directory(input_dir, output_csv)

    assert len(results) == 2
    assert output_csv.exists()
    assert results[0]["filename"] == "paper1.docx"
    assert results[1]["filename"] == "paper2.docx"


def test_empty_directory_generates_empty_csv(tmp_path):
    input_dir = tmp_path / "empty"
    input_dir.mkdir()

    output_csv = tmp_path / "results.csv"

    results = process_directory(input_dir, output_csv)

    assert results == []
    assert output_csv.exists()
