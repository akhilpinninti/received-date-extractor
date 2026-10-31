
from pathlib import Path

from docx import Document

from received_date_extractor.file_validator import (
    validate_docx,
    validate_directory,
)


def create_docx(path: Path):
    document = Document()
    document.add_paragraph("Test manuscript")
    document.save(path)


def test_valid_docx(tmp_path):
    path = tmp_path / "valid.docx"
    create_docx(path)

    result = validate_docx(path)

    assert result["is_valid"] is True
    assert result["errors"] == []


def test_missing_file(tmp_path):
    result = validate_docx(tmp_path / "missing.docx")

    assert result["is_valid"] is False


def test_invalid_extension(tmp_path):
    path = tmp_path / "document.pdf"
    path.write_text("test")

    result = validate_docx(path)

    assert result["is_valid"] is False


def test_empty_file(tmp_path):
    path = tmp_path / "empty.docx"
    path.write_bytes(b"")

    result = validate_docx(path)

    assert result["is_valid"] is False


def test_corrupted_docx(tmp_path):
    path = tmp_path / "corrupted.docx"
    path.write_bytes(b"Not a valid DOCX")

    result = validate_docx(path)

    assert result["is_valid"] is False


def test_directory_validation(tmp_path):
    create_docx(tmp_path / "second.docx")
    create_docx(tmp_path / "first.docx")

    results = validate_directory(tmp_path)

    assert len(results) == 2
    assert all(result["is_valid"] for result in results)


def test_invalid_directory(tmp_path):
    results = validate_directory(tmp_path / "missing")

    assert results == []
