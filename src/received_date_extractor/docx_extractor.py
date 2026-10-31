
"""Extract structured text from DOCX manuscripts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from docx import Document
from docx.document import Document as DocumentObject
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn


def _extract_paragraph(
    paragraph: Paragraph,
    location: str,
    index: int,
) -> dict[str, Any]:
    return {
        "text": paragraph.text.strip(),
        "location": location,
        "index": index,
        "style": paragraph.style.name if paragraph.style else None,
    }


def _extract_table(
    table: Table,
    location: str,
    start_index: int,
) -> list[dict[str, Any]]:
    blocks = []
    index = start_index

    for row_index, row in enumerate(table.rows):
        for cell_index, cell in enumerate(row.cells):
            for paragraph in cell.paragraphs:
                text = paragraph.text.strip()

                if text:
                    blocks.append({
                        "text": text,
                        "location": location,
                        "index": index,
                        "table_row": row_index,
                        "table_cell": cell_index,
                    })
                    index += 1

    return blocks


def _extract_body_in_order(
    document: DocumentObject,
) -> list[dict[str, Any]]:
    """Extract body paragraphs and tables in document order."""
    blocks = []
    paragraph_index = 0
    table_index = 0

    body = document.element.body

    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            paragraph = Paragraph(child, document)
            text = paragraph.text.strip()

            if text:
                blocks.append(
                    _extract_paragraph(
                        paragraph,
                        "body",
                        paragraph_index,
                    )
                )
                paragraph_index += 1

        elif child.tag == qn("w:tbl"):
            table = Table(child, document)

            table_blocks = _extract_table(
                table,
                "body_table",
                paragraph_index,
            )

            blocks.extend(table_blocks)
            paragraph_index += len(table_blocks)
            table_index += 1

    return blocks


def _extract_headers_footers(
    document: DocumentObject,
) -> list[dict[str, Any]]:
    blocks = []
    index = 0

    for section_index, section in enumerate(document.sections):
        header = section.header

        for paragraph in header.paragraphs:
            text = paragraph.text.strip()

            if text:
                blocks.append({
                    "text": text,
                    "location": "header",
                    "section_index": section_index,
                    "index": index,
                })
                index += 1

        for table in header.tables:
            table_blocks = _extract_table(
                table,
                "header_table",
                index,
            )
            blocks.extend(table_blocks)
            index += len(table_blocks)

        footer = section.footer

        for paragraph in footer.paragraphs:
            text = paragraph.text.strip()

            if text:
                blocks.append({
                    "text": text,
                    "location": "footer",
                    "section_index": section_index,
                    "index": index,
                })
                index += 1

        for table in footer.tables:
            table_blocks = _extract_table(
                table,
                "footer_table",
                index,
            )
            blocks.extend(table_blocks)
            index += len(table_blocks)

    return blocks


def extract_docx(file_path: str | Path) -> dict[str, Any]:
    """
    Extract text blocks from a DOCX manuscript.

    The caller should validate the file before extraction.
    """
    path = Path(file_path)

    document = Document(path)

    body_blocks = _extract_body_in_order(document)
    header_footer_blocks = _extract_headers_footers(document)

    all_blocks = body_blocks + header_footer_blocks

    return {
        "filename": path.name,
        "file_path": str(path),
        "blocks": all_blocks,
        "total_blocks": len(all_blocks),
        "body_blocks": len(body_blocks),
        "header_footer_blocks": len(header_footer_blocks),
    }
