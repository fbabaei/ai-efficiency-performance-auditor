import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from auditor_tools.budgets import evaluate_budgets
from auditor_tools.otlp import normalize_otlp


ROOT = Path(__file__).resolve().parents[1]


def otlp_span(index: int = 1) -> dict:
    return {
        "traceId": "a" * 32,
        "spanId": f"{index:016x}",
        "startTimeUnixNano": "1000000000000000000",
        "endTimeUnixNano": "1000000000001000000",
        "name": "PRIVATE prompt must never appear",
        "status": {"code": 1, "message": "PRIVATE provider message"},
        "attributes": [
            {"key": "gen_ai.operation.name", "value": {"stringValue": "chat"}},
            {"key": "gen_ai.usage.input_tokens", "value": {"intValue": "12"}},
            {"key": "gen_ai.input.messages", "value": {"stringValue": "PRIVATE content"}},
        ],
        "events": [{"name": "PRIVATE event"}],
    }


def trace_document(*spans: dict) -> dict:
    return {"resourceSpans": [{
        "resource": {"attributes": [{"key": "secret", "value": {"stringValue": "PRIVATE"}}]},
        "scopeSpans": [{"spans": list(spans)}],
    }]}


def measurements(count: int = 20) -> dict:
    return {
        "schema": "auditor-measurements/1",
        "scenario": "search",
        "workload_id": "dataset-1",
        "quality_contract_id": "quality-1",
        "conditions_id": "conditions-1",
        "currency": "USD",
        "coverage": "complete",
        "requests": [
            {
                "id": f"request-{index}",
                "success": True,
                "latency_ms": index + 1,
                "tool_attempts": 2,
                "model_attempts": 1,
                "input_tokens": 12,
                "output_tokens": 4,
                "cost": 0.02,
            }
            for index in range(count)
        ],
    }


def budgets() -> dict:
    return {
        "schema": "auditor-budgets/1",
        "approved": True,
        "scenario": "search",
        "quality_contract_id": "quality-1",
        "currency": "USD",
        "limits": [
            {"metric": "success_rate", "min": 0.95},
            {"metric": "latency_p95_ms", "max": 20},
            {"metric": "cost_per_successful_task", "max": 0.03},
        ],
    }


class OtlpImportTests(unittest.TestCase):
    def test_metadata_only_with_exact_nanosecond_duration_and_unknown_usage(self) -> None:
        result = normalize_otlp(trace_document(otlp_span()), source_id="capture-1")
        serialized = json.dumps(result)
        self.assertNotIn("PRIVATE", serialized)
        self.assertEqual(result["schema"], "auditor-traces/1")
        self.assertEqual(result["coverage"], "unknown")
        span = result["spans"][0]
        self.assertEqual(span["duration_ms"], 1)
        self.assertEqual(span["input_tokens"], 12)
        self.assertIsNone(span["output_tokens"])
        self.assertEqual(span["operation"], "chat")
        self.assertEqual(span["status"], "ok")
        self.assertEqual(span["source_record"], "resourceSpans/0/scopeSpans/0/spans/0")

    def test_same_span_id_in_different_traces_and_explicit_duplicate_exports(self) -> None:
        first = otlp_span()
        other = otlp_span()
        other["traceId"] = "b" * 32
        result = normalize_otlp(trace_document(first, copy.deepcopy(first), other), source_id="s1")
        self.assertEqual(len(result["spans"]), 2)
        self.assertEqual(result["duplicates_removed"], 1)
        conflicting = copy.deepcopy(first)
        conflicting["endTimeUnixNano"] = "1000000000002000000"
        with self.assertRaisesRegex(ValueError, "conflicting"):
            normalize_otlp(trace_document(first, conflicting), source_id="s1")

    def test_missing_timing_and_unrecognized_operation_stay_unknown(self) -> None:
        span = otlp_span()
        del span["startTimeUnixNano"]
        span["attributes"][0]["value"]["stringValue"] = "PRIVATE custom operation"
        result = normalize_otlp(trace_document(span), source_id="s1")
        self.assertIsNone(result["spans"][0]["duration_ms"])
        self.assertEqual(result["spans"][0]["operation"], "unknown")
        self.assertNotIn("PRIVATE", json.dumps(result))

    def test_rejects_bad_ids_timestamps_usage_and_ambiguous_attributes(self) -> None:
        changes = (
            {"traceId": "0" * 32},
            {"spanId": "../bad"},
            {"parentSpanId": "x" * 16},
            {"startTimeUnixNano": True},
            {"endTimeUnixNano": "1"},
            {"status": {"code": "STATUS_CODE_OK"}},
            {"attributes": [{"key": "gen_ai.usage.input_tokens", "value": {"intValue": "-1"}}]},
            {"attributes": [
                {"key": "gen_ai.usage.input_tokens", "value": {"intValue": "1"}},
                {"key": "gen_ai.usage.input_tokens", "value": {"intValue": "2"}},
            ]},
        )
        for change in changes:
            with self.subTest(change=change):
                span = otlp_span()
                span.update(change)
                with self.assertRaises(ValueError):
                    normalize_otlp(trace_document(span), source_id="s1")
        with self.assertRaises(ValueError):
            normalize_otlp({"resource_spans": []}, source_id="s1")


class BudgetGateTests(unittest.TestCase):
    def test_exact_thresholds_and_cost_of_failed_requests_are_counted(self) -> None:
        run = measurements()
        run["requests"][0]["success"] = False
        result = evaluate_budgets(run, budgets())
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["metrics"]["success_rate"], 0.95)
        self.assertAlmostEqual(result["metrics"]["cost_per_successful_task"], 0.4 / 19)
        self.assertEqual(result["metrics"]["latency_p95_ms"], 19)
        self.assertEqual(result["metrics"]["tool_attempts_per_request"], 2)

    def test_unknowns_and_partial_coverage_do_not_pass(self) -> None:
        for count, field, value in (
            (19, None, None),
            (20, "success", None),
            (20, "cost", None),
        ):
            run = measurements(count)
            if field:
                run["requests"][0][field] = value
            with self.subTest(count=count, field=field):
                self.assertEqual(evaluate_budgets(run, budgets())["status"], "inconclusive")
        for coverage in ("partial", "unknown"):
            run = measurements()
            run["coverage"] = coverage
            self.assertEqual(evaluate_budgets(run, budgets())["status"], "inconclusive")
        run = measurements()
        for request in run["requests"]:
            request["success"] = False
        result = evaluate_budgets(run, budgets())
        self.assertIsNone(result["metrics"]["cost_per_successful_task"])
        self.assertEqual(result["status"], "fail")

    def test_quality_regression_fails_even_when_cost_is_lower(self) -> None:
        run = measurements()
        run["requests"][0]["success"] = False
        run["requests"][1]["success"] = False
        for request in run["requests"]:
            request["cost"] = 0.001
        self.assertEqual(evaluate_budgets(run, budgets())["status"], "fail")

    def test_decimal_threshold_equality_is_not_a_rounding_regression(self) -> None:
        run = measurements(6)
        for request in run["requests"]:
            request["cost"] = 0.1
        policy = budgets()
        policy["limits"] = [
            {"metric": "success_rate", "min": 0.95},
            {"metric": "cost_per_request", "max": 0.1},
        ]
        self.assertEqual(evaluate_budgets(run, policy)["status"], "pass")

    def test_regression_requires_comparability_and_nonzero_baseline(self) -> None:
        policy = budgets()
        policy["limits"].append({
            "metric": "tool_attempts_per_request", "max_relative_increase": 0.1,
        })
        baseline = measurements()
        candidate = measurements()
        for request in candidate["requests"]:
            request["tool_attempts"] = 3
        self.assertEqual(evaluate_budgets(candidate, policy, baseline)["status"], "inconclusive")
        result = evaluate_budgets(candidate, policy, baseline, comparable=True)
        self.assertEqual(result["status"], "fail")
        baseline["conditions_id"] = "different"
        self.assertEqual(
            evaluate_budgets(candidate, policy, baseline, comparable=True)["status"],
            "inconclusive",
        )
        baseline = measurements()
        for request in baseline["requests"]:
            request["tool_attempts"] = 0
        self.assertEqual(
            evaluate_budgets(candidate, policy, baseline, comparable=True)["status"],
            "inconclusive",
        )

    def test_invalid_or_unapproved_inputs_are_explicit_errors(self) -> None:
        for mutation in (
            lambda run, policy: policy.update(approved=False),
            lambda run, policy: policy["limits"].pop(0),
            lambda run, policy: policy["limits"][0].update(min=True),
            lambda run, policy: policy["limits"][0].update(min=1.1),
            lambda run, policy: policy["limits"][1].update(metric="invented"),
            lambda run, policy: run["requests"][0].update(cost=float("nan")),
            lambda run, policy: run["requests"][0].update(tool_attempts=True),
            lambda run, policy: run["requests"].append(copy.deepcopy(run["requests"][0])),
            lambda run, policy: run.update(currency="EUR"),
        ):
            run, policy = measurements(), budgets()
            mutation(run, policy)
            with self.subTest(run=run, policy=policy), self.assertRaises(ValueError):
                evaluate_budgets(run, policy)


class OfflineCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "auditor_tools", *args],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )

    def test_import_confirmation_and_exclusive_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "trace.json"
            target = Path(directory) / "normalized.json"
            source.write_text(json.dumps(trace_document(otlp_span())), encoding="utf-8")
            args = ("import-otlp", str(source), "--output", str(target))
            self.assertEqual(self.run_cli(*args).returncode, 2)
            self.assertFalse(target.exists())
            result = self.run_cli(*args, "--confirm-sanitized")
            self.assertEqual(result.returncode, 0, result.stderr)
            original = target.read_bytes()
            self.assertNotIn(b"PRIVATE", original)
            self.assertEqual(self.run_cli(*args, "--confirm-sanitized").returncode, 2)
            self.assertEqual(target.read_bytes(), original)
            source.write_text('{"resourceSpans":[],"resourceSpans":[]}', encoding="utf-8")
            self.assertEqual(
                self.run_cli("import-otlp", str(source), "--confirm-sanitized").returncode, 2,
            )

    def test_gate_cli_exit_codes_and_machine_readable_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_path = Path(directory) / "run.json"
            policy_path = Path(directory) / "policy.json"
            policy_path.write_text(json.dumps(budgets()), encoding="utf-8")
            for count, success, expected in ((20, True, 0), (20, False, 1), (19, True, 3)):
                run = measurements(count)
                for request in run["requests"]:
                    request["success"] = success
                run_path.write_text(json.dumps(run), encoding="utf-8")
                result = self.run_cli("gate", str(run_path), "--budgets", str(policy_path))
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertIn(json.loads(result.stdout)["status"], ("pass", "fail", "inconclusive"))
            policy_path.write_text('{"schema":"auditor-budgets/1","approved":NaN}', encoding="utf-8")
            result = self.run_cli("gate", str(run_path), "--budgets", str(policy_path))
            self.assertEqual(result.returncode, 2)
            self.assertTrue(result.stderr)
            self.assertEqual(result.stdout, "")

    def test_documented_examples_run_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "trace.json"
            example = ROOT / "examples" / "offline"
            imported = self.run_cli(
                "import-otlp", str(example / "traces.json"),
                "--confirm-sanitized", "--output", str(target),
            )
            self.assertEqual(imported.returncode, 0, imported.stderr)
            self.assertEqual(len(json.loads(target.read_text(encoding="utf-8"))["spans"]), 1)
            args = (
                "gate", str(example / "candidate.json"), "--budgets", str(example / "budgets.json"),
                "--baseline", str(example / "baseline.json"),
            )
            self.assertEqual(self.run_cli(*args).returncode, 3)
            checked = self.run_cli(*args, "--confirm-comparable")
            self.assertEqual(checked.returncode, 0, checked.stderr)
            result = json.loads(checked.stdout)
            self.assertEqual(result["metrics"]["latency_p95_ms"], 10)
            self.assertEqual(result["metrics"]["cost_per_successful_task"], 0.02)
            self.assertEqual(result["metrics"]["tool_attempts_per_request"], 2)


if __name__ == "__main__":
    unittest.main()
