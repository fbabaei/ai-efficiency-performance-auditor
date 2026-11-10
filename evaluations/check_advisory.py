"""Score selected advisory-skill companions; not independent evidence aggregation."""

import argparse
import json
import math
from pathlib import Path

from evaluations.check_reporting import check_summary


FIXTURES = Path(__file__).resolve().parent / "advisory_cases.json"


def _metric_equal(value: object, expected: object) -> bool:
    if expected is None:
        return value is None
    if type(expected) in (int, float):
        return (
            type(value) in (int, float)
            and (type(value) is int or math.isfinite(value))
            and value == expected
        )
    return type(value) is type(expected) and value == expected


def check_advisory(report: object) -> list[str]:
    if not isinstance(report, dict) or set(report) != {
        "case", "assessment", "metrics", "finding_categories", "evidence",
        "detailed_report", "executive_summary",
    }:
        return ["capture fields must match the advisory evaluation envelope"]
    cases = json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]
    case = report["case"]
    if not isinstance(case, str):
        return ["case must name a synthetic advisory case"]
    expected = next((item for item in cases if item["id"] == case), None)
    if expected is None:
        return ["unknown advisory case"]
    errors = []
    if report["assessment"] != expected["assessment"]:
        errors.append("assessment does not match the scenario evidence")
    metrics = report["metrics"]
    if not isinstance(metrics, dict) or set(metrics) != set(expected["metrics"]):
        errors.append("metric fields must match this scenario")
    else:
        for field, value in expected["metrics"].items():
            if not _metric_equal(metrics[field], value):
                errors.append(f"{field} must preserve the supported value or unknown")
    if report["finding_categories"] != expected["finding_categories"]:
        errors.append("missing supported finding or false-positive ranked finding")
    evidence = report["evidence"]
    if (
        not isinstance(evidence, list)
        or not all(isinstance(item, str) for item in evidence)
        or sorted(evidence) != sorted(expected["required_evidence"])
    ):
        errors.append("evidence must cite exactly the supplied scenario references")
    detailed = report["detailed_report"]
    if not isinstance(detailed, str) or not detailed.strip():
        errors.append("detailed_report must contain the captured Markdown")
    summary = report["executive_summary"]
    if not isinstance(summary, str) or not summary.strip():
        errors.append("executive_summary must contain the captured Markdown")
    else:
        rows, summary_errors = check_summary(summary)
        errors.extend(summary_errors)
        if len(rows) != len(expected["finding_categories"]):
            errors.append("summary priority rows must match demonstrated findings only")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path, help="captured advisory evaluation envelope")
    args = parser.parse_args()
    try:
        report = json.loads(
            args.capture.read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_object,
        )
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"Cannot read capture: {error}\n")
    errors = check_advisory(report)
    if errors:
        print("\n".join(f"FAIL: {error}" for error in errors))
        return 1
    print("PASS: synthetic advisory companion matches selected contract checks.")
    print("Manually verify Markdown fidelity, semantic evidence, tool scope and host behavior.")
    return 0


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


if __name__ == "__main__":
    raise SystemExit(main())
