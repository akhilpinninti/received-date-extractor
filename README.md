# Received Date Extractor

An automated Python-based tool to extract manuscript received dates from Microsoft Word (`.docx`) documents and generate a standardized CSV report.

## 1. Project Overview

The objective of this project is to identify the original manuscript received date from a collection of DOCX manuscripts.

The system extracts document content, detects date candidates, identifies their context, normalizes valid dates, and determines whether a received date can be selected reliably.

The final submission CSV follows this format:

```csv
file,received_date
manuscript_01.docx,2026-01-02
manuscript_02.docx,INVALID
```

### Output rules

- Each DOCX file must have exactly one corresponding row.
- Successfully identified dates must use the `YYYY-MM-DD` format.
- If a reliable received date cannot be identified, the output must contain `INVALID`.
- Dates referring to manuscript acceptance, publication, revision, supporting files, or unrelated events must not be incorrectly selected as the original received date.
- Ambiguous or conflicting dates must not be guessed.

## 2. Current Implementation Status

The following components have been implemented:

- DOCX file validation.
- Extraction of paragraphs, tables, headers, and footers.
- Date pattern detection.
- Received-date context identification.
- Date normalization and calendar validation.
- Decision engine for selecting received dates.
- Detailed internal CSV generation.
- Command-line interface.
- Ubuntu execution script.
- Automated unit and integration tests.
- Automated test report generation.

### Current test results

| Metric | Result |
|---|---:|
| Sample DOCX manuscripts | 20 |
| Automated tests | 93 |
| Tests passed | 93 |
| Tests failed | 0 |
| Dates extracted in current regression run | 9 |
| Invalid or unresolved results | 11 |

**Important:** Passing automated tests does not mean that extraction accuracy across all 20 sample manuscripts is complete. Some real manuscript dates are still being missed and are part of the next development phase.

## 3. Project Structure

```text
received-date-extractor/
│
├── README.md
├── main.py
├── run.sh
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── scripts/
│   ├── inspect_manuscripts.py
│   └── generate_test_report.py
│
├── src/
│   └── received_date_extractor/
│       ├── __init__.py
│       ├── config.py
│       ├── csv_generator.py
│       ├── date_detector.py
│       ├── date_normalizer.py
│       ├── decision_engine.py
│       ├── docx_extractor.py
│       ├── file_validator.py
│       ├── manuscript_inspector.py
│       └── pipeline.py
│
├── tests/
│   ├── test_config.py
│   ├── test_csv_generator.py
│   ├── test_date_detector.py
│   ├── test_date_normalizer.py
│   ├── test_decision_engine.py
│   ├── test_docx_extractor.py
│   ├── test_file_validator.py
│   ├── test_manuscript_inspector.py
│   └── test_pipeline.py
│
├── manuscripts/
│   └── Sample DOCX manuscripts
│
├── data/
│   └── output/
│
├── test_report.csv
└── test-results.xml
```

Virtual environments and Python cache directories are excluded from version control.

## 4. Description of Important Files

### Root-level files

| File | Purpose |
|---|---|
| `main.py` | Command-line entry point. Accepts an input folder and output CSV path, processes DOCX files, and writes the required two-column submission CSV. |
| `run.sh` | Executes the project in an Ubuntu environment using Python 3.12. Creates a virtual environment and installs dependencies when needed. |
| `requirements.txt` | Contains the Python dependencies required by the project. |
| `pyproject.toml` | Contains pytest configuration, test directory settings, and Python source path configuration. |
| `.gitignore` | Prevents virtual environments, cache files, temporary data, and other generated files from being committed. |
| `README.md` | Project documentation and execution instructions. |

### Source code: `src/received_date_extractor/`

| File | Purpose |
|---|---|
| `config.py` | Defines project configuration, supported file extensions, date settings, and processing options. |
| `file_validator.py` | Validates input paths and checks whether DOCX files are valid and accessible. |
| `docx_extractor.py` | Extracts text from DOCX paragraphs, tables, headers, and footers. |
| `manuscript_inspector.py` | Inspects manuscript content and organizes extracted text blocks with their metadata and locations. |
| `date_detector.py` | Identifies date patterns and evaluates their surrounding textual context. |
| `date_normalizer.py` | Converts recognized dates into standardized date values and checks calendar validity. |
| `decision_engine.py` | Determines whether a candidate can be selected as the received date or requires further review. |
| `csv_generator.py` | Generates the detailed internal CSV containing processing results and candidate information. |
| `pipeline.py` | Connects the validation, inspection, detection, normalization, decision, and reporting stages. |

### Scripts

| File | Purpose |
|---|---|
| `scripts/inspect_manuscripts.py` | Inspects sample manuscripts and generates information useful for understanding document structures and date patterns. |
| `scripts/generate_test_report.py` | Reads pytest's JUnit XML output and generates the required `test_report.csv`. |

### Tests

| File | Purpose |
|---|---|
| `test_config.py` | Tests configuration values and settings. |
| `test_file_validator.py` | Tests valid, missing, empty, and corrupted input files. |
| `test_docx_extractor.py` | Tests extraction of paragraphs, tables, headers, and footers. |
| `test_manuscript_inspector.py` | Tests document inspection, metadata, and structural handling. |
| `test_date_detector.py` | Tests date-pattern recognition and context identification. |
| `test_date_normalizer.py` | Tests date conversion, ambiguity, and calendar validation. |
| `test_decision_engine.py` | Tests received-date selection, conflicts, and review decisions. |
| `test_csv_generator.py` | Tests CSV creation and output formatting. |
| `test_pipeline.py` | Tests the complete manuscript-processing pipeline. |

### Generated files

| File | Purpose |
|---|---|
| `test_report.csv` | Required five-column report containing automated test results. |
| `test-results.xml` | JUnit XML report generated by pytest. |
| `data/output/submission_test.csv` | Current regression output for the 20 sample manuscripts. |

## 5. Technologies and Dependencies

- Python 3.12
- python-docx
- python-dateutil
- dateparser
- lxml
- pytest
- pytest-cov

Development and testing environments:

- Visual Studio Code
- Ubuntu 24.04.1 LTS through WSL
- Git and GitHub

## 6. Installation and Setup

### Prerequisites

Install:

- Python 3.12
- Git
- Ubuntu environment with Python virtual environment support

On Ubuntu 24.04, install the required virtual environment package:

```bash
sudo apt update
sudo apt install -y python3.12-venv
```

Clone the repository:

```bash
git clone https://github.com/akhilpinninti/received-date-extractor.git
```

Navigate into the project:

```bash
cd received-date-extractor
```

Make the runner executable:

```bash
chmod +x run.sh
```

## 7. Running the Project

The project accepts two command-line arguments:

1. Input directory containing DOCX manuscripts.
2. Destination path for the output CSV.

### Execute using the provided runner

```bash
./run.sh manuscripts data/output/submission_test.csv
```

The runner:

1. Checks the supplied arguments.
2. Validates the input directory.
3. Checks for Python 3.12.
4. Creates the Linux virtual environment if it does not exist.
5. Installs the required dependencies.
6. Configures the Python source path.
7. Executes `main.py`.

### Expected output

The program displays:

```text
Total DOCX files: 20
Dates extracted: <count>
Invalid or unresolved: <count>
CSV created: <output path>
```

The exact counts depend on the input manuscripts and current extraction implementation.

### Inspect the generated CSV

```bash
cat data/output/submission_test.csv
```

To display the first ten lines:

```bash
head -n 10 data/output/submission_test.csv
```

To count the rows:

```bash
wc -l data/output/submission_test.csv
```

For 20 DOCX files, the expected line count is 21, including the header.

## 8. Running Automated Tests

Activate no environment manually if using the following command:

```bash
.venv-linux/bin/python -m pytest -v
```

To generate the JUnit XML report while running the tests:

```bash
.venv-linux/bin/python -m pytest -v --junitxml=test-results.xml
```

The current automated test suite contains 93 tests, all of which passed in the latest recorded run.

## 9. Generating the Required Test Report

The required report must be generated at the repository root.

First, execute:

```bash
.venv-linux/bin/python -m pytest -v --junitxml=test-results.xml
```

Then generate the CSV:

```bash
.venv-linux/bin/python scripts/generate_test_report.py
```

Verify the output:

```bash
head -n 10 test_report.csv
wc -l test_report.csv
```

### Test report format

The report uses the following exact columns:

```csv
checks,input,expected,actual,result
```

Each automated test is represented by one row.

- `checks`: Name of the automated test.
- `input`: Test module or test class.
- `expected`: Expected successful test outcome.
- `actual`: Actual test execution outcome.
- `result`: PASS, FAIL, or SKIP.

The current report contains 93 test entries, plus the header.

## 10. Current Limitations and Planned Improvements

Although the initial implementation and automated tests are complete, the system still requires improvements in real-world manuscript extraction.

The following scenarios are targeted for the next development phase:

1. Improve received-date extraction from headers and footers.
2. Improve date extraction from tables and nested tables.
3. Handle dates written in different textual formats.
4. Improve recognition of numeric dates with two-digit years.
5. Handle ambiguous day/month ordering without making unsupported assumptions.
6. Distinguish original manuscript received dates from dates associated with supporting documents and attachments.
7. Handle multiple received-date candidates in the same manuscript.
8. Improve handling of unusual formatting, line breaks, and fragmented text.
9. Avoid false positives from ordinary sentences containing words such as "received".
10. Improve error handling for corrupted or unsupported DOCX files.
11. Expand regression tests using the supplied sample manuscripts.
12. Improve extraction accuracy without weakening the existing validation and decision safeguards.

### Specific regression cases requiring further investigation

| Manuscript | Known issue |
|---|---|
| `merged_13.docx` | Received date in header is currently not extracted. |
| `merged_14.docx` | A received date is present but currently returns INVALID. |
| `merged_15.docx` | Received date in a table is currently not extracted. |
| `merged_18.docx` | Numeric date with a two-digit year is currently unresolved. |

These cases will be investigated and addressed in subsequent development iterations.

The corrupted sample `merged_12.docx` will also remain an invalid-input test case unless a valid source document is provided.

## 11. Development Roadmap

### Phase 1 — Initial implementation

- Project architecture.
- DOCX validation.
- Document text extraction.
- Date detection and normalization.
- Received-date decision engine.
- CSV generation.
- Automated testing.

**Status: Implemented.**

### Phase 2 — Submission infrastructure

- Root-level Ubuntu `run.sh`.
- Python 3.12 environment setup.
- Command-line execution.
- Required submission CSV.
- Automated test report generation.

**Status: Implemented and tested.**

### Phase 3 — Extraction accuracy improvements

- Investigate all unresolved sample manuscripts.
- Improve header, footer, and table handling.
- Improve date pattern coverage.
- Improve context classification.
- Reduce false positives.
- Add regression tests for every identified edge case.

**Status: In progress.**

### Phase 4 — Final validation

- Run all automated tests.
- Reprocess all 20 sample manuscripts.
- Compare actual output against expected received dates.
- Verify CSV structure and date formatting.
- Verify clean Ubuntu execution.
- Update documentation.
- Commit and push the final implementation.

**Status: Planned.**

### Phase 5 — Final submission

- Verify the GitHub repository.
- Include source code, tests, README, and required reports.
- Export and include the relevant ChatGPT conversation.
- Perform a final repository and submission checklist.

**Status: Pending.**

## 12. Git and GitHub Workflow

Repository:

https://github.com/akhilpinninti/received-date-extractor

Check the current Git status:

```bash
git status
```

Stage changes:

```bash
git add .
```

Review staged changes:

```bash
git diff --cached --stat
```

Commit:

```bash
git commit -m "Describe your changes"
```

Push:

```bash
git push origin main
```

Check synchronization:

```bash
git status
```

Do not commit virtual environments, temporary caches, or private sample manuscripts.

## 13. Final Output Requirements

The final submission must include:

- Working Python source code.
- Automated tests.
- Root-level `README.md`.
- Root-level executable `run.sh`.
- Root-level `test_report.csv`.
- Required submission CSV with the exact header `file,received_date`.
- One output row for every DOCX file.
- ISO-formatted dates or `INVALID`.
- Exported ChatGPT conversation.

---

**Project repository:** https://github.com/akhilpinninti/received-date-extractor

**Current development focus:** Improving received-date extraction accuracy across different manuscript structures and date formats while maintaining reliable validation and decision-making.
