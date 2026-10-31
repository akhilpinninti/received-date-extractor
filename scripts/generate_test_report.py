import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

xml_file = Path("test-results.xml")
report_file = Path("test_report.csv")

if not xml_file.exists():
    sys.exit("ERROR: Run pytest with --junitxml=test-results.xml first.")

root = ET.parse(xml_file).getroot()
cases = list(root.iter("testcase"))

with report_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["checks", "input", "expected", "actual", "result"])

    for case in cases:
        name = f"{case.get('classname', '')}.{case.get('name', '')}"
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")

        if failure is not None:
            actual = "FAIL: " + (failure.get("message") or "Test failed")
            result = "FAIL"
        elif error is not None:
            actual = "ERROR: " + (error.get("message") or "Test error")
            result = "FAIL"
        elif skipped is not None:
            actual = "SKIPPED"
            result = "SKIP"
        else:
            actual = "PASS"
            result = "PASS"

        writer.writerow([name, case.get("classname", ""), "PASS", actual, result])

print(f"Total checks: {len(cases)}")
print(f"Passed: {sum(1 for c in cases if c.find('failure') is None and c.find('error') is None and c.find('skipped') is None)}")
print(f"Report generated: {report_file.resolve()}")
