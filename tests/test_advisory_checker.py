import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evaluations.check_advisory import FIXTURES, check_advisory


ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]
HEADER = (
    "| Priority | Weak area | Code location | Recommended improvement | Expected benefit | Evidence |\n"
    "|---|---|---|---|---|---|\n"
)


def oracle(case: dict) -> dict:
    rows = "".join(
        f"| P1 | {category} | {case['required_evidence'][0]} | Conditional reuse "
        "| Static conditional benefit only | Synthetic checker input |\n"
        for category in case["finding_categories"]
    )
    return {
        "case": case["id"],
        "assessment": case["assessment"],
        "metrics": copy.deepcopy(case["metrics"]),
        "finding_categories": case["finding_categories"].copy(),
        "evidence": case["required_evidence"].copy(),
        "detailed_report": "Synthetic checker oracle, not a model capture or verified audit.",
        "executive_summary": "# Executive Summary\n\n" + HEADER + rows,
    }


class AdvisoryCheckerTests(unittest.TestCase):
    def test_synthetic_cases_have_unique_ids_and_installed_skills(self) -> None:
        self.assertEqual(len({case["id"] for case in CASES}), len(CASES))
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["input"])
                self.assertTrue(
                    (ROOT / ".github" / "skills" / case["skill"] / "SKILL.md").is_file()
                )
                self.assertEqual(check_advisory(oracle(case)), [])

    def test_fixture_arithmetic_is_independently_consistent(self) -> None:
        cases = {case["id"]: case for case in CASES}
        metrics = cases["comparison-matched"]["metrics"]
        baseline, candidate = 80 / 20, 120 / 40
        self.assertEqual(metrics["baseline_calls_per_request"], baseline)
        self.assertEqual(metrics["candidate_calls_per_request"], candidate)
        self.assertEqual(metrics["delta_calls_per_request"], candidate - baseline)
        self.assertEqual(metrics["percent_change"], 100 * (candidate - baseline) / baseline)
        self.assertEqual(
            cases["orchestration-nested-retry-bound"]["metrics"]["conditional_transport_attempt_bound"],
            2 * 3,
        )
        self.assertEqual(
            cases["orchestration-mutually-exclusive-retries"]["metrics"]["conditional_attempt_upper_bound"],
            max(2, 3),
        )
        self.assertEqual(cases["comparison-zero-baseline"]["metrics"]["percent_change"], "N/A")
        for case in CASES:
            if case["assessment"] in {"not-comparable", "not-verifiable", "no-demonstrated-waste"}:
                self.assertEqual(case["finding_categories"], [])

    def test_rejects_malformed_missing_or_unknown_envelopes(self) -> None:
        for value in (None, {}, [], "invalid", True):
            self.assertTrue(check_advisory(value))
        for field in oracle(CASES[0]):
            report = oracle(CASES[0])
            del report[field]
            with self.subTest(field=field):
                self.assertTrue(check_advisory(report))
        for value in (None, [], {}, True, "unknown"):
            report = oracle(CASES[0])
            report["case"] = value
            self.assertTrue(check_advisory(report))

    def test_rejects_invented_counts_and_numeric_unknowns(self) -> None:
        for case in CASES:
            for field in case["metrics"]:
                for value in (True, "0", -999, float("nan"), float("inf"), 10**400):
                    report = oracle(case)
                    report["metrics"][field] = value
                    with self.subTest(case=case["id"], field=field, value_type=type(value).__name__):
                        self.assertTrue(check_advisory(report))
                if case["metrics"][field] is None:
                    report = oracle(case)
                    report["metrics"][field] = 0
                    self.assertTrue(check_advisory(report))

    def test_rejects_wrong_assessments_findings_and_evidence(self) -> None:
        for case in CASES:
            for field, value in (
                ("assessment", "improved"),
                ("finding_categories", ["invented-saving"]),
                ("evidence", []),
                ("evidence", ["unrelated-record"]),
                ("evidence", [case["required_evidence"][0]] * 3),
                ("metrics", {}),
            ):
                report = oracle(case)
                report[field] = value
                with self.subTest(case=case["id"], field=field):
                    self.assertTrue(check_advisory(report))

    def test_rejects_summary_findings_for_negative_cases_and_missing_positive(self) -> None:
        for case in CASES:
            report = oracle(case)
            if case["finding_categories"]:
                report["executive_summary"] = "# Executive Summary\n\n" + HEADER
            else:
                report["executive_summary"] += (
                    "| P1 | Invented | Unknown | Remove | Unverified | No evidence |\n"
                )
            with self.subTest(case=case["id"]):
                self.assertTrue(check_advisory(report))

    def test_reuses_summary_limits_and_requires_captured_text(self) -> None:
        for field in ("detailed_report", "executive_summary"):
            for value in (None, [], {}, "", " "):
                report = oracle(CASES[0])
                report[field] = value
                self.assertTrue(check_advisory(report))
        for suffix in ("\n" * 61, " word" * 601, "\n```\nsource()\n```"):
            report = oracle(CASES[0])
            report["executive_summary"] += suffix
            self.assertTrue(check_advisory(report))

    def test_cli_exit_codes_and_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.json"
            command = [sys.executable, "-m", "evaluations.check_advisory", str(path)]
            for content, code in (
                (json.dumps(oracle(CASES[0])), 0),
                ("{}", 1),
                ("{", 2),
                ('{"case": "comparison-matched", "case": "comparison-confounded"}', 2),
            ):
                path.write_text(content, encoding="utf-8-sig")
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
                with self.subTest(code=code, content=content[:25]):
                    self.assertEqual(result.returncode, code)
            path.unlink()
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
