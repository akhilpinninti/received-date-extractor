from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
REPORT_DIR = OUTPUT_DIR / "reports"

# Supported manuscript format
SUPPORTED_EXTENSIONS = {".docx"}

# Date interpretation
DEFAULT_DATE_ORDER = None  # None means ambiguous numeric dates require review

# Date detection settings
CONTEXT_KEYWORDS = {
    "received": ("received", "date received", "submitted"),
    "revised": ("revised", "revision received"),
    "accepted": ("accepted",),
    "published": ("published", "publication date"),
}

# Decision settings
MANUAL_REVIEW_ON_CONFLICT = True
MANUAL_REVIEW_ON_AMBIGUOUS_DATE = True

# CSV output
CSV_FILENAME = "received_dates.csv"
CSV_ENCODING = "utf-8-sig"

# Processing
RECURSIVE_SCAN = False