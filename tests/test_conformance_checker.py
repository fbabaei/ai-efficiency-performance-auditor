import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evaluations.check_conformance import AREAS, SECTIONS, check_conformance


ROOT = Path(__file__).resolve().parents[1]
ORACLES = json.loads(
    (ROOT / "evaluations" / "conformance_cases.json").read_text(encoding="utf-8")
)["cases"]


def reference_capture(case: str = "completed-review") -> dict:
    return copy.deepcopy(next(item for item in ORACLES if item["case"] == case))


class ConformanceCheckerTests(unittest.TestCase):
    def test_accepts_all_synthetic_oracles(self) -> None:
        for capture in ORACLES:
            with self.subTest(case=capture["case"]):
                self.assertEqual(check_conformance(capture), [])

    def test_oracle_totals_are_independently_consistent(self) -> None:
        capture = reference_capture()
        metrics = capture["metrics"]
        self.assertEqual(sum(metrics["request_attempts"]), metrics["attempts"])
        self.assertEqual(sum(metrics["outcomes"].values()), metrics["attempts"])
        self.assertGreaterEqual(metrics["attempts"], metrics["logical_calls"])
        for field in ("input", "cached_input", "output", "reasoning"):
            self.assertEqual(
                sum(row[field] for row in metrics["usage"]["rows"]),
                metrics["usage"]["totals"][field],
            )
        self.assertEqual({row["area"] for row in capture["coverage"]}, AREAS)

    def test_rejects_malformed_envelopes(self) -> None:
        for value in (None, [], {}, True, "completed-review"):
            with self.subTest(value=value):
                self.assertTrue(check_conformance(value))
        for field in reference_capture():
            capture = reference_capture()
            del capture[field]
            with self.subTest(missing=field):
                self.assertTrue(check_conformance(capture))
        for case in (None, True, [], {}, "unknown"):
            capture = reference_capture()
            capture["case"] = case
            with self.subTest(case=case):
                self.assertTrue(check_conformance(capture))
        capture = reference_capture()
        capture["unexpected"] = True
        self.assertTrue(check_conformance(capture))

    def test_stops_require_reasons_scope_and_checked_paths(self) -> None:
        for oracle in ORACLES[:3]:
            for old in ("Search scope:", "Paths checked:", ".toml", ".json"):
                capture = copy.deepcopy(oracle)
                capture["response"] = capture["response"].replace(old, "")
                if capture != oracle:
                    with self.subTest(case=oracle["case"], missing=old):
                        self.assertTrue(check_conformance(capture))
            for field in ("response", "detailed_report", "executive_summary", "metrics", "coverage"):
                capture = copy.deepcopy(oracle)
                capture[field] = "" if field == "response" else "unexpected report/count"
                with self.subTest(case=oracle["case"], field=field):
                    self.assertTrue(check_conformance(capture))

    def test_stops_reject_explicit_call_counts(self) -> None:
        for count in (
            "0 calls", "two model calls", "3 logical tool calls", "one attempt",
            "Calls: 2", "Model attempts = zero", "logical_calls: 2",
        ):
            capture = reference_capture("missing-application")
            capture["response"] += "\n" + count
            with self.subTest(count=count):
                self.assertTrue(check_conformance(capture))

    def test_stops_reject_reports_embedded_in_chat(self) -> None:
        for heading in ("## Executive Summary", "## Runtime metrics", "**Ranked findings**"):
            capture = reference_capture("missing-application")
            capture["response"] += "\n" + heading + "\nUnexpected audit content."
            with self.subTest(heading=heading):
                self.assertTrue(check_conformance(capture))

    def test_allows_a_report_title_and_requires_supplied_summary_findings(self) -> None:
        capture = reference_capture()
        capture["detailed_report"] = "# Synthetic audit\n\n" + capture["detailed_report"]
        self.assertEqual(check_conformance(capture), [])
        capture["impact"] = []
        self.assertTrue(check_conformance(capture))

    def test_rejects_malformed_nested_shapes_without_crashing(self) -> None:
        for field in ("coverage", "metrics", "impact"):
            for value in (None, {}, True, "invalid"):
                capture = reference_capture()
                capture[field] = value
                with self.subTest(field=field, value=value):
                    self.assertTrue(check_conformance(capture))
        for field in ("outcomes", "statistics", "usage", "savings"):
            for value in (None, [], True, "invalid"):
                capture = reference_capture()
                capture["metrics"][field] = value
                with self.subTest(field=field, value=value):
                    self.assertTrue(check_conformance(capture))
        for field in ("coverage", "impact"):
            capture = reference_capture()
            capture[field] = [[], None, True]
            self.assertTrue(check_conformance(capture))

    def test_requires_ordered_sections_and_valid_summary(self) -> None:
        for section in SECTIONS:
            capture = reference_capture()
            capture["detailed_report"] = capture["detailed_report"].replace(section, "Other")
            with self.subTest(section=section):
                self.assertTrue(check_conformance(capture))
        for field in ("detailed_report", "executive_summary", "response"):
            for value in (None, [], {}, "", " "):
                capture = reference_capture()
                capture[field] = value
                with self.subTest(field=field, value=value):
                    self.assertTrue(check_conformance(capture))
        for suffix in ("\n" * 61, " word" * 601, "\n```\nsource()\n```"):
            capture = reference_capture()
            capture["executive_summary"] += suffix
            with self.subTest(suffix=suffix[:10]):
                self.assertTrue(check_conformance(capture))

    def test_section_headings_cannot_be_hidden_in_comments_or_code(self) -> None:
        for prefix, suffix in (("<!--\n", "\n-->"), ("````markdown\n", "\n````"), ("~~~\n", "\n~~~")):
            capture = reference_capture()
            capture["detailed_report"] = prefix + capture["detailed_report"] + suffix
            with self.subTest(prefix=prefix):
                self.assertTrue(check_conformance(capture))
        capture = reference_capture()
        capture["detailed_report"] += "\n````python\n## Ranked findings\n```\n````\n"
        self.assertEqual(check_conformance(capture), [])
        capture["detailed_report"] += "\n## Ranked findings\n"
        self.assertTrue(check_conformance(capture))

    def test_coverage_cannot_omit_duplicate_or_invent_areas(self) -> None:
        for rows in ([], reference_capture()["coverage"][:-1]):
            capture = reference_capture()
            capture["coverage"] = rows
            self.assertTrue(check_conformance(capture))
        for area in ("invented", [], None, "orchestration"):
            capture = reference_capture()
            capture["coverage"][-1]["area"] = area
            with self.subTest(area=area):
                self.assertTrue(check_conformance(capture))

    def test_coverage_statuses_require_evidence_or_explanation(self) -> None:
        for field, value in (
            ("status", "complete"), ("status", []), ("evidence", []),
            ("evidence", [None]), ("evidence", "src/pipeline.py"), ("gap", "unknown"),
        ):
            capture = reference_capture()
            capture["coverage"][0][field] = value
            with self.subTest(field=field, value=value):
                self.assertTrue(check_conformance(capture))
        for status in ("partial", "missing", "not-applicable"):
            capture = reference_capture()
            row = capture["coverage"][0]
            row["status"] = status
            row["gap"] = None
            row["evidence"] = ["source"] if status == "partial" else []
            with self.subTest(status=status):
                self.assertTrue(check_conformance(capture))
            row["gap"] = "Specific limitation or applicability rationale."
            self.assertEqual(check_conformance(capture), [])

    def test_counts_outcomes_and_disjoint_rows_reconcile(self) -> None:
        for field, value in (
            ("logical_calls", 41), ("logical_calls", True), ("attempts", 41),
            ("attempts", -1), ("attempts", 40.0), ("attempts", 2**53),
            ("outcomes", {}), ("request_attempts", []), ("request_attempts", [True]),
        ):
            capture = reference_capture()
            capture["metrics"][field] = value
            with self.subTest(field=field, value=value):
                self.assertTrue(check_conformance(capture))
        for value in (39, True, "40", -1):
            capture = reference_capture()
            capture["metrics"]["outcomes"]["succeeded"] = value
            self.assertTrue(check_conformance(capture))

    def test_request_statistics_enforce_five_and_twenty_request_thresholds(self) -> None:
        for count in (1, 4, 5, 19, 20):
            capture = reference_capture()
            metrics = capture["metrics"]
            metrics["logical_calls"] = metrics["attempts"] = 2 * count
            metrics["outcomes"]["succeeded"] = 2 * count
            metrics["request_attempts"] = [2] * count
            metrics["statistics"] = {
                "mean": 2 if count >= 5 else None,
                "median": 2 if count >= 5 else None,
                "p95": 2 if count >= 20 else None,
                "percentile_method": "nearest-rank" if count >= 20 else None,
            }
            metrics["savings"].update(baseline=2 * count, proposed=count, combined_savings=count)
            with self.subTest(count=count):
                self.assertEqual(check_conformance(capture), [])
            metrics["statistics"]["p95"] = None if count >= 20 else 2
            self.assertTrue(check_conformance(capture))

    def test_recomputes_percentiles_and_rejects_nonfinite_statistics(self) -> None:
        capture = reference_capture()
        metrics = capture["metrics"]
        metrics["request_attempts"] = [1] * 19 + [21]
        metrics["statistics"].update(mean=2, median=1, p95=1)
        self.assertEqual(check_conformance(capture), [])
        for field in ("mean", "median", "p95"):
            for value in (float("nan"), float("inf"), True, -1, 100):
                changed = copy.deepcopy(capture)
                changed["metrics"]["statistics"][field] = value
                with self.subTest(field=field, value=value):
                    self.assertTrue(check_conformance(changed))
        capture = reference_capture()
        capture["metrics"]["statistics"]["p95"] = 2.000000001
        self.assertTrue(check_conformance(capture))
        capture = reference_capture()
        capture["metrics"]["logical_calls"] = 0
        self.assertTrue(check_conformance(capture))

    def test_token_subsets_and_missing_usage_are_not_added_or_zeroed(self) -> None:
        for field, value in (("input", 180), ("output", 20), ("reasoning", True)):
            capture = reference_capture()
            capture["metrics"]["usage"]["totals"][field] = value
            self.assertTrue(check_conformance(capture))
        for subset, value in (("cached_input", 101), ("reasoning", 11)):
            capture = reference_capture()
            capture["metrics"]["usage"]["rows"][0][subset] = value
            self.assertTrue(check_conformance(capture))
        capture = reference_capture()
        capture["metrics"]["usage"]["rows"][0]["input"] = None
        capture["metrics"]["usage"]["totals"]["input"] = None
        self.assertEqual(check_conformance(capture), [])
        capture["metrics"]["usage"]["totals"]["input"] = 50
        self.assertTrue(check_conformance(capture))
        for field, value in (("id", "oracle-model-1"), ("input", True), ("output", 5.0)):
            capture = reference_capture()
            capture["metrics"]["usage"]["rows"][1][field] = value
            self.assertTrue(check_conformance(capture))

    def test_savings_do_not_mix_units_or_exceed_the_baseline(self) -> None:
        for field, value in (
            ("unit", "tokens"), ("baseline", 41), ("proposed", 41),
            ("combined_savings", 41), ("combined_savings", True), ("combined_savings", 11),
        ):
            capture = reference_capture()
            capture["metrics"]["savings"][field] = value
            with self.subTest(field=field, value=value):
                self.assertTrue(check_conformance(capture))

    def test_absent_frequency_precludes_workload_ranking_and_numeric_traffic_impact(self) -> None:
        capture = reference_capture()
        row = capture["impact"][0]
        row.update(branch_frequency=None, frequency_evidence=None, workload_weighted=None)
        capture["ranking_scope"] = "scenario"
        self.assertEqual(check_conformance(capture), [])
        row["workload_weighted"] = 0
        self.assertTrue(check_conformance(capture))
        row["workload_weighted"] = None
        capture["ranking_scope"] = "workload"
        self.assertTrue(check_conformance(capture))

    def test_frequency_requires_evidence_and_consistent_weighted_impact(self) -> None:
        for field, value in (
            ("branch_frequency", -0.5), ("branch_frequency", 1.5),
            ("branch_frequency", True), ("branch_frequency", float("nan")),
            ("frequency_evidence", ""), ("workload_weighted", 1),
            ("scenario_local", -1), ("unit", "USD"),
        ):
            capture = reference_capture()
            capture["impact"][0][field] = value
            with self.subTest(field=field, value=value):
                self.assertTrue(check_conformance(capture))
        capture = reference_capture()
        capture["impact"][0].update(scenario_local=None, workload_weighted=None)
        self.assertEqual(check_conformance(capture), [])
        capture["impact"].append(copy.deepcopy(capture["impact"][0]))
        self.assertTrue(check_conformance(capture))

    def test_cli_exit_codes_and_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.json"
            command = [sys.executable, "-m", "evaluations.check_conformance", str(path)]
            for contents, code, message in (
                (json.dumps(reference_capture()), 0, "PASS:"),
                ("{}", 1, "FAIL:"),
                ("{", 2, "Cannot read capture:"),
                ('{"case": "scope-required", "case": "missing-application"}', 2, "duplicate JSON key"),
            ):
                path.write_text(contents, encoding="utf-8-sig")
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
                with self.subTest(code=code, contents=contents[:30]):
                    self.assertEqual(result.returncode, code)
                    self.assertIn(message, result.stdout + result.stderr)
            path.unlink()
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
