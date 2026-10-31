import json
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from received_date_extractor.manuscript_inspector import (
    inspect_directory,
    inspect_manuscript,
    save_inspection_report,
)


def _save_document(path: Path, text: str = "") -> None:
    document = Document()
    if text:
        document.add_paragraph(text)
    document.save(path)


def test_valid_docx_with_paragraphs(tmp_path: Path) -> None:
    path = tmp_path / "ordinary.docx"
    _save_document(path, "A manuscript paragraph.")

    result = inspect_manuscript(path)

    assert result["status"] == "VALID"
    assert result["paragraph_count"] == 1
    assert result["extracted_text"][0]["text"] == "A manuscript paragraph."


def test_docx_containing_table(tmp_path: Path) -> None:
    path = tmp_path / "table.docx"
    document = Document()
    table = document.add_table(rows=1, cols=1)
    table.cell(0, 0).text = "Table content"
    document.save(path)

    result = inspect_manuscript(path)

    assert result["status"] == "VALID"
    assert result["table_count"] == 1
    assert any(item["text"] == "Table content" for item in result["extracted_text"])


def test_header_and_footer_are_inspected(tmp_path: Path) -> None:
    path = tmp_path / "header-footer.docx"
    document = Document()
    document.sections[0].header.paragraphs[0].text = "Header content"
    document.sections[0].footer.paragraphs[0].text = "Footer content"
    document.save(path)

    result = inspect_manuscript(path)

    assert result["header_count"] == 1
    assert result["footer_count"] == 1
    assert any(item["location"].startswith("header") for item in result["extracted_text"])
    assert any(item["location"].startswith("footer") for item in result["extracted_text"])


def test_distinct_first_page_and_even_page_headers_and_footers(tmp_path: Path) -> None:
    path = tmp_path / "header-variants.docx"
    document = Document()
    section = document.sections[0]
    section.different_first_page_header_footer = True
    even_setting = OxmlElement("w:evenAndOddHeaders")
    document.settings._element.append(even_setting)
    section.header.paragraphs[0].text = "Default header"
    section.first_page_header.paragraphs[0].text = "First header"
    section.even_page_header.paragraphs[0].text = "Even header"
    section.footer.paragraphs[0].text = "Default footer"
    section.first_page_footer.paragraphs[0].text = "First footer"
    section.even_page_footer.paragraphs[0].text = "Even footer"
    document.save(path)

    result = inspect_manuscript(path)
    texts = {item["text"] for item in result["extracted_text"]}

    assert {"Default header", "First header", "Even header"} <= texts
    assert {"Default footer", "First footer", "Even footer"} <= texts
    assert result["header_count"] == 3
    assert result["footer_count"] == 3


def test_linked_headers_and_footers_are_processed_once(tmp_path: Path) -> None:
    path = tmp_path / "linked.docx"
    document = Document()
    first = document.sections[0]
    second = document.add_section()
    first.header.paragraphs[0].text = "Shared header"
    first.footer.paragraphs[0].text = "Shared footer"
    assert second.header.is_linked_to_previous
    assert second.footer.is_linked_to_previous
    document.save(path)

    result = inspect_manuscript(path)

    assert result["header_count"] == 1
    assert result["footer_count"] == 1
    assert sum(item["text"] == "Shared header" for item in result["extracted_text"]) == 1


def test_nested_table_content(tmp_path: Path) -> None:
    path = tmp_path / "nested.docx"
    document = Document()
    outer_cell = document.add_table(rows=1, cols=1).cell(0, 0)
    nested_table = outer_cell.add_table(rows=1, cols=1)
    nested_table.cell(0, 0).text = "Nested content"
    document.save(path)

    result = inspect_manuscript(path)

    assert any(item["text"] == "Nested content" for item in result["extracted_text"])


def test_merged_cells_are_not_repeated(tmp_path: Path) -> None:
    path = tmp_path / "merged.docx"
    document = Document()
    table = document.add_table(rows=2, cols=3)
    table.cell(0, 0).text = "Horizontal merge"
    table.cell(0, 0).merge(table.cell(0, 1))
    table.cell(0, 2).text = "Vertical merge"
    table.cell(0, 2).merge(table.cell(1, 2))
    document.save(path)

    result = inspect_manuscript(path)
    texts = [item["text"] for item in result["extracted_text"]]

    assert texts.count("Horizontal merge") == 1
    assert texts.count("Vertical merge") == 1


def test_source_indices_and_keyword_metadata(tmp_path: Path) -> None:
    path = tmp_path / "metadata.docx"
    document = Document()
    document.add_paragraph("Before")
    document.add_paragraph("Received in paragraph")
    table = document.add_table(rows=1, cols=1)
    table.cell(0, 0).text = "Accepted in table"
    document.add_paragraph("After")
    document.save(path)

    result = inspect_manuscript(path)
    paragraph = next(item for item in result["extracted_text"] if item["text"] == "Received in paragraph")
    table_cell = next(item for item in result["extracted_text"] if item["text"] == "Accepted in table")
    occurrence = next(item for item in result["keyword_occurrences"] if item["keyword"] == "Received")

    assert paragraph["paragraph_index"] == 1
    assert table_cell["table_index"] == 0
    assert table_cell["row_index"] == 0
    assert table_cell["cell_index"] == 0
    assert occurrence["paragraph_index"] == 1
    assert occurrence["snippet"] == "Received in paragraph"


def test_documents_without_special_xml_structures(tmp_path: Path) -> None:
    path = tmp_path / "ordinary-xml.docx"
    _save_document(path, "No special structures")

    result = inspect_manuscript(path)

    assert result["special_xml_structures"] == {
        "text_boxes": False,
        "footnotes": False,
        "endnotes": False,
    }


def test_keyword_detection_includes_snippets(tmp_path: Path) -> None:
    path = tmp_path / "keywords.docx"
    _save_document(path, "Received Revised Accepted Published")

    result = inspect_manuscript(path)

    assert [item["keyword"] for item in result["keyword_occurrences"]] == [
        "Received",
        "Revised",
        "Accepted",
        "Published",
    ]
    assert all(item["snippet"] for item in result["keyword_occurrences"])


def test_corrupted_docx(tmp_path: Path) -> None:
    path = tmp_path / "corrupt.docx"
    path.write_bytes(b"not a DOCX archive")

    result = inspect_manuscript(path)

    assert result["status"] == "INVALID_DOCX"
    assert result["error_message"]


def test_missing_file(tmp_path: Path) -> None:
    result = inspect_manuscript(tmp_path / "missing.docx")

    assert result["status"] == "NOT_FOUND"
    assert result["error_message"]


def test_empty_but_valid_docx(tmp_path: Path) -> None:
    _save_document(tmp_path / "empty.docx")

    result = inspect_manuscript(tmp_path / "empty.docx")

    assert result["status"] == "VALID"
    assert result["paragraph_count"] == 0
    assert result["keyword_occurrences"] == []


def test_directory_results_are_sorted(tmp_path: Path) -> None:
    for name in ("merged_02.docx", "merged_01.docx"):
        _save_document(tmp_path / name, name)

    results = inspect_directory(tmp_path)

    assert [result["filename"] for result in results] == [
        "merged_01.docx",
        "merged_02.docx",
    ]


def test_json_report_generation_and_serialization(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    output = tmp_path / "data" / "report.json"
    _save_document(source, "Unicode: résumé")

    results = [inspect_manuscript(source)]
    save_inspection_report(results, output)

    serialized = json.loads(output.read_text(encoding="utf-8"))
    assert serialized == results
    assert "résumé" in output.read_text(encoding="utf-8")
