"""Run manuscript inspection for the project's manuscript directory."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from received_date_extractor.manuscript_inspector import (  # noqa: E402
    inspect_directory,
    save_inspection_report,
)


def main() -> None:
    manuscript_directory = PROJECT_ROOT / "manuscripts"
    output_path = PROJECT_ROOT / "data" / "output" / "manuscript_inspection.json"
    results = inspect_directory(manuscript_directory)
    save_inspection_report(results, output_path)
    valid_count = sum(result["status"] == "VALID" for result in results)
    invalid_count = sum(result["status"] != "VALID" for result in results)
    print(
        f"Processed {len(results)} files: "
        f"{valid_count} valid, {invalid_count} invalid."
    )


if __name__ == "__main__":
    main()
