"""Command-line interface for received-date extraction."""

import argparse
import csv
import sys
from pathlib import Path

from received_date_extractor.pipeline import process_manuscript


def main():
    parser = argparse.ArgumentParser(
        description="Extract received dates from DOCX manuscripts."
    )
    parser.add_argument("input_folder")
    parser.add_argument("output_csv")
    args = parser.parse_args()

    input_path = Path(args.input_folder)

    if not input_path.is_dir():
        print(f"ERROR: Input directory does not exist: {input_path}")
        return 2

    files = sorted(
        [
            p for p in input_path.iterdir()
            if p.is_file() and p.suffix.lower() == ".docx"
        ],
        key=lambda p: p.name.lower()
    )

    output_path = Path(args.output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    success = 0
    invalid = 0

    with output_path.open(
        "w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["file", "received_date"])

        for file_path in files:
            result = process_manuscript(file_path)

            date = (
                result.get("selected_date")
                if result.get("status") == "SUCCESS"
                else None
            )

            if date:
                success += 1
                output_date = date
            else:
                invalid += 1
                output_date = "INVALID"

            writer.writerow([file_path.name, output_date])

    print(f"Total DOCX files: {len(files)}")
    print(f"Dates extracted: {success}")
    print(f"Invalid or unresolved: {invalid}")
    print(f"CSV created: {output_path.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
