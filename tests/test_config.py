from pathlib import Path

from received_date_extractor import config


def test_project_root_is_path():
    assert isinstance(config.PROJECT_ROOT, Path)


def test_data_directories_are_inside_project():
    assert config.DATA_DIR == config.PROJECT_ROOT / "data"
    assert config.INPUT_DIR == config.DATA_DIR / "input"
    assert config.OUTPUT_DIR == config.DATA_DIR / "output"
    assert config.REPORT_DIR == config.OUTPUT_DIR / "reports"


def test_supported_extensions():
    assert ".docx" in config.SUPPORTED_EXTENSIONS


def test_default_date_order_requires_no_assumption():
    assert config.DEFAULT_DATE_ORDER is None


def test_context_keywords_are_configured():
    assert "received" in config.CONTEXT_KEYWORDS
    assert "revised" in config.CONTEXT_KEYWORDS
    assert "accepted" in config.CONTEXT_KEYWORDS
    assert "published" in config.CONTEXT_KEYWORDS


def test_manual_review_settings():
    assert config.MANUAL_REVIEW_ON_CONFLICT is True
    assert config.MANUAL_REVIEW_ON_AMBIGUOUS_DATE is True


def test_csv_settings():
    assert config.CSV_FILENAME.endswith(".csv")
    assert config.CSV_ENCODING == "utf-8-sig"


def test_recursive_scan_setting():
    assert isinstance(config.RECURSIVE_SCAN, bool)