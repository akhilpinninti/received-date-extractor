
from pathlib import Path

from docx import Document

from received_date_extractor.docx_extractor import extract_docx


def test_extract_paragraphs(tmp_path):
    path = tmp_path / "sample.docx"

    document = Document()
    document.add_paragraph("Received on 12 January 2025")
    document.add_paragraph("Accepted on 20 March 2025")
    document.save(path)

    result = extract_docx(path)

    assert result["total_blocks"] >= 2
    assert any(
        "Received on 12 January 2025" in block["text"]
        for block in result["blocks"]
    )


def test_extract_table_content(tmp_path):
    path = tmp_path / "table.docx"

    document = Document()
    table = document.add_table(rows=1, cols=2)

    table.cell(0, 0).text = "Received"
    table.cell(0, 1).text = "12 January 2025"

    document.save(path)

    result = extract_docx(path)

    assert any(
        "12 January 2025" in block["text"]
        and block["location"] == "body_table"
        for block in result["blocks"]
    )


def test_extract_header(tmp_path):
    path = tmp_path / "header.docx"

    document = Document()
    document.sections[0].header.paragraphs[0].text = (
        "Received on 12 January 2025"
    )
    document.save(path)

    result = extract_docx(path)

    assert any(
        "Received on 12 January 2025" in block["text"]
        and block["location"] == "header"
        for block in result["blocks"]
    )


def test_extract_footer(tmp_path):
    path = tmp_path / "footer.docx"

    document = Document()
    document.sections[0].footer.paragraphs[0].text = (
        "Accepted on 20 March 2025"
    )
    document.save(path)

    result = extract_docx(path)

    assert any(
        "Accepted on 20 March 2025" in block["text"]
        and block["location"] == "footer"
        for block in result["blocks"]
    )


def test_empty_document(tmp_path):
    path = tmp_path / "empty.docx"

    document = Document()
    document.save(path)

    result = extract_docx(path)

    assert result["filename"] == "empty.docx"
    assert result["total_blocks"] == 0


def test_extraction_metadata(tmp_path):
    path = tmp_path / "metadata.docx"

    document = Document()
    document.add_paragraph("Sample manuscript")
    document.save(path)

    result = extract_docx(path)

    assert result["filename"] == "metadata.docx"
    assert result["file_path"] == str(path)
    assert "blocks" in result
    assert result["total_blocks"] == len(result["blocks"])
