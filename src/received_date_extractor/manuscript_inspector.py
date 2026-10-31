"""Inspection utilities for Word manuscript documents."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any, Iterator

from docx import Document
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph

KEYWORDS = ("Received", "Revised", "Accepted", "Published")
_KEYWORD_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(keyword) for keyword in KEYWORDS) + r")\b",
    re.IGNORECASE,
)
_SNIPPET_RADIUS = 60


def _element_path(element: Any) -> str:
    """Return a stable XML path for an element within its document part."""
    return element.getroottree().getpath(element)


def _cell_text(cell: _Cell) -> str:
    """Return direct paragraph text from a cell, excluding nested tables."""
    return "\n".join(
        Paragraph(block, cell).text
        for block in cell._element.iterchildren()
        if block.tag.endswith("}p")
    )


def _iter_table_records(
    table: Table,
    table_index: int,
    seen_cells: set[str],
    next_table_index: Iterator[int],
    location_prefix: str = "table",
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row_index, row in enumerate(table.rows):
        for cell_index, cell in enumerate(row.cells):
            cell_key = _element_path(cell._tc)
            if cell_key not in seen_cells:
                seen_cells.add(cell_key)
                records.append(
                    {
                        "location": location_prefix,
                        "table_index": table_index,
                        "row_index": row_index,
                        "cell_index": cell_index,
                        "text": _cell_text(cell),
                    }
                )
            for block in cell._element.iterchildren():
                if block.tag.endswith("}tbl"):
                    nested_index = next(next_table_index)
                    records.extend(
                        _iter_table_records(
                            Table(block, cell),
                            nested_index,
                            seen_cells,
                            next_table_index,
                            location_prefix,
                        )
                    )
    return records


def _iter_body_records(document: Any) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    paragraph_index = 0
    table_counter = iter(range(0, 1_000_000))
    seen_cells: set[str] = set()
    for block in document._element.body.iterchildren():
        if block.tag.endswith("}p"):
            records.append(
                {
                    "location": "paragraph",
                    "paragraph_index": paragraph_index,
                    "text": Paragraph(block, document).text,
                }
            )
            paragraph_index += 1
        elif block.tag.endswith("}tbl"):
            table_index = next(table_counter)
            records.extend(
                _iter_table_records(
                    Table(block, document),
                    table_index,
                    seen_cells,
                    table_counter,
                )
            )
    return records, paragraph_index


def _iter_header_footer_records(
    container: Any,
    section_index: int,
    variant: str,
    seen_cells: set[str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for paragraph in container.paragraphs:
        records.append(
            {
                "location": "header" if "header" in variant else "footer",
                "section_index": section_index,
                "variant": variant,
                "text": paragraph.text,
            }
        )
    table_counter = iter(range(0, 1_000_000))
    for table in container.tables:
        records.extend(
            _iter_table_records(
                table,
                next(table_counter),
                seen_cells,
                table_counter,
                location_prefix="header" if "header" in variant else "footer",
            )
        )
    return records


def _part_identifier(container: Any) -> str:
    """Return the stable package identifier for a header/footer part."""
    return str(container.part.partname)


def _keyword_occurrences(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    occurrences: list[dict[str, Any]] = []
    for record in records:
        text = record["text"]
        for match in _KEYWORD_PATTERN.finditer(text):
            start = max(0, match.start() - _SNIPPET_RADIUS)
            end = min(len(text), match.end() + _SNIPPET_RADIUS)
            occurrence = dict(record)
            occurrence.update(
                keyword=match.group(1),
                snippet=text[start:end].strip(),
            )
            occurrences.append(occurrence)
    return occurrences


def _special_xml_structures(path: Path) -> dict[str, bool]:
    structures = {
        "text_boxes": False,
        "footnotes": False,
        "endnotes": False,
    }
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        structures["footnotes"] = "word/footnotes.xml" in names
        structures["endnotes"] = "word/endnotes.xml" in names
        for name in names:
            if name.endswith(".xml") and b"w:txbxContent" in archive.read(name):
                structures["text_boxes"] = True
                break
    return structures


def inspect_manuscript(file_path: str | Path) -> dict[str, Any]:
    """Inspect one DOCX file without raising document-level processing errors."""
    path = Path(file_path)
    result: dict[str, Any] = {
        "filename": path.name,
        "status": "NOT_FOUND",
        "paragraph_count": 0,
        "table_count": 0,
        "header_count": 0,
        "footer_count": 0,
        "extracted_text_length": 0,
        "keyword_occurrences": [],
        "extracted_text": [],
        "special_xml_structures": {
            "text_boxes": False,
            "footnotes": False,
            "endnotes": False,
        },
        "error_message": None,
    }
    if not path.exists():
        result["error_message"] = f"File not found: {path}"
        return result
    try:
        document = Document(path)
        body_records, paragraph_count = _iter_body_records(document)
        all_records = list(body_records)
        result["paragraph_count"] = paragraph_count
        result["table_count"] = len(document.tables)

        seen_parts: set[str] = set()
        seen_cells: set[str] = set()
        variants = [("default", "header", "header"), ("default", "footer", "footer")]
        if document.settings._element.find(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}evenAndOddHeaders"
        ) is not None:
            variants.extend(
                [
                    ("even_page", "even_page_header", "header"),
                    ("even_page", "even_page_footer", "footer"),
                ]
            )
        for section_index, section in enumerate(document.sections):
            section_variants = list(variants)
            if section.different_first_page_header_footer:
                section_variants.extend(
                    [
                        ("first_page", "first_page_header", "header"),
                        ("first_page", "first_page_footer", "footer"),
                    ]
                )
            for variant, attribute, kind in section_variants:
                container = getattr(section, attribute)
                part_id = _part_identifier(container)
                if part_id in seen_parts:
                    continue
                seen_parts.add(part_id)
                records = _iter_header_footer_records(
                    container, section_index, f"{variant}_{kind}", seen_cells
                )
                all_records.extend(records)
                if kind == "header":
                    result["header_count"] += 1
                else:
                    result["footer_count"] += 1

        result["extracted_text"] = all_records
        result["extracted_text_length"] = sum(
            len(record["text"]) for record in all_records
        )
        result["keyword_occurrences"] = _keyword_occurrences(all_records)
        result["special_xml_structures"] = _special_xml_structures(path)
        result["status"] = "VALID"
    except Exception as exc:
        result["status"] = "INVALID_DOCX"
        result["error_message"] = str(exc)
    return result


def inspect_directory(directory_path: str | Path) -> list[dict[str, Any]]:
    """Inspect all DOCX files in a directory in sorted filename order."""
    directory = Path(directory_path)
    if not directory.exists():
        return []
    paths = sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() == ".docx"
        ),
        key=lambda path: path.name.lower(),
    )
    return [inspect_manuscript(path) for path in paths]


def save_inspection_report(
    results: list[dict[str, Any]], output_path: str | Path
) -> None:
    """Serialize inspection results as readable UTF-8 JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
