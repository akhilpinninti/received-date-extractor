
"""Validation utilities for Microsoft Word DOCX manuscripts."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any


REQUIRED_DOCX_FILES = {
    "[Content_Types].xml",
    "word/document.xml",
}


def validate_docx(file_path: str | Path) -> dict[str, Any]:
    """
    Validate whether a file is a structurally readable DOCX document.

    Returns a dictionary containing validation status and error details.
    """
    path = Path(file_path)

    result: dict[str, Any] = {
        "filename": path.name,
        "file_path": str(path),
        "is_valid": False,
        "errors": [],
    }

    if not path.exists():
        result["errors"].append("File does not exist.")
        return result

    if not path.is_file():
        result["errors"].append("Path does not point to a file.")
        return result

    if path.suffix.lower() != ".docx":
        result["errors"].append("Unsupported file extension. Expected .docx.")
        return result

    if path.stat().st_size == 0:
        result["errors"].append("File is empty.")
        return result

    if not zipfile.is_zipfile(path):
        result["errors"].append("File is not a valid DOCX ZIP archive.")
        return result

    try:
        with zipfile.ZipFile(path, "r") as archive:
            file_names = set(archive.namelist())

            encrypted_files = [
                info.filename
                for info in archive.infolist()
                if info.flag_bits & 0x1
            ]

            if encrypted_files:
                result["errors"].append(
                    "DOCX archive contains encrypted files."
                )
                return result

            missing_files = REQUIRED_DOCX_FILES - file_names

            if missing_files:
                result["errors"].append(
                    "Missing required DOCX components: "
                    + ", ".join(sorted(missing_files))
                )
                return result

            corrupted_file = archive.testzip()

            if corrupted_file is not None:
                result["errors"].append(
                    f"Corrupted content inside DOCX archive: {corrupted_file}"
                )
                return result

    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        result["errors"].append(
            f"Unable to read DOCX archive: {exc}"
        )
        return result

    result["is_valid"] = True
    return result


def validate_directory(directory_path: str | Path) -> list[dict[str, Any]]:
    """Validate all DOCX files in a directory in sorted order."""
    directory = Path(directory_path)

    if not directory.exists() or not directory.is_dir():
        return []

    files = sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() == ".docx"
        ),
        key=lambda path: path.name.lower(),
    )

    return [validate_docx(path) for path in files]
