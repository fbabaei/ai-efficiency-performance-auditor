"""Check captured review companions, not tool execution or semantic correctness."""

import argparse
import json
import math
from pathlib import Path
import re
import statistics

from evaluations.check_reporting import check_summary


AREAS = {
    "orchestration", "tools-retries", "models-context", "output-consumption",
    "safety", "runtime-evidence",
}
SECTIONS = (
    "Verdict and evidence coverage", "Call map and inventory", "Runtime metrics",
    "Ranked findings", "Proposed design", "Validation plan and missing evidence",
)
STOP_CASES = {
    "scope-required": (
        "scope selection required",
        ("apps/alpha/pyproject.toml", "apps/beta/pyproject.toml"),
    ),
    "missing-application": ("not auditable", ("apps/missing/pyproject.toml",)),
    "trace-unconfirmed": ("not auditable", ("traces/unmarked.json",)),
}
USAGE_FIELDS = {"input", "cached_input", "output", "reasoning"}
MAX_INTEGER = 2**53 - 1


def _object(value: object, keys: set[str], label: str, errors: list[str]) -> dict | None:
    if not isinstance(value, dict) or set(value) != keys:
        errors.append(f"{label}: fields must match {', '.join(sorted(keys))}")
        return None
    return value


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _count(value: object) -> bool:
    return type(value) is int and 0 <= value <= MAX_INTEGER


def _number(value: object) -> bool:
    return _count(value) or (
        type(value) is float and math.isfinite(value) and 0 <= value <= MAX_INTEGER
    )


def _equal(value: object, expected: int | float | None) -> bool:
    if expected is None:
        return value is None
    if type(value) is not int and type(value) is not float:
        return False
    if type(expected) is int:
        return _number(value) and value == expected
    return _number(value) and math.isclose(value, expected, rel_tol=1e-9, abs_tol=1e-12)


def _section_headings(text: str) -> list[str]:
    headings = []
    fence: tuple[str, int] | None = None
    text = re.sub(r"<!--[\s\S]*?-->", "", text)
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is not None:
            if (
                marker is not None
                and marker[1][0] == fence[0]
                and len(marker[1]) >= fence[1]
                and not marker[2].strip()
            ):
                fence = None
            continue
        if marker is not None:
            fence = (marker[1][0], len(marker[1]))
            continue
        heading = re.match(r"^#{1,6}\s+(?:[1-6]\.\s+)?(.+?)\s*$", line)
        if heading is not None and heading[1] in SECTIONS:
            headings.append(heading[1])
    return headings


def _coverage(value: object, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("coverage must be an array")
        return
    seen = set()
    for item in value:
        row = _object(item, {"area", "status", "evidence", "gap"}, "coverage row", errors)
        if row is None:
            continue
        area = row["area"]
        if not isinstance(area, str) or area not in AREAS or area in seen:
            errors.append("coverage areas must be known, unique and complete")
        else:
            seen.add(area)
        status = row["status"]
        if not isinstance(status, str) or status not in {
            "inspected", "partial", "missing", "not-applicable",
        }:
            errors.append("invalid coverage status")
            continue
        evidence = row["evidence"]
        if not isinstance(evidence, list) or not all(_text(ref) for ref in evidence):
            errors.append("coverage evidence must be an array of nonempty references")
            continue
        if status in {"inspected", "partial"} and not evidence:
            errors.append("inspected/partial coverage requires evidence")
        if status in {"missing", "not-applicable"} and evidence:
            errors.append("missing/not-applicable coverage must not invent evidence")
        if status == "inspected":
            if row["gap"] is not None:
                errors.append("inspected coverage must have a null gap")
        elif not _text(row["gap"]):
            errors.append("partial/missing/not-applicable coverage requires a gap or rationale")
    if seen != AREAS:
        errors.append("coverage must contain all six areas")


def _usage(value: object, errors: list[str]) -> None:
    usage = _object(value, {"semantics", "rows", "totals"}, "usage", errors)
    if usage is None:
        return
    if usage["semantics"] != "input-includes-cache;output-includes-reasoning":
        errors.append("this case requires the declared token-subset semantics")
    rows = usage["rows"]
    totals = _object(usage["totals"], USAGE_FIELDS, "usage totals", errors)
    if not isinstance(rows, list) or not rows:
        errors.append("usage rows must contain the inspected model-attempt records")
        return
    valid_rows = []
    seen = set()
    for item in rows:
        row = _object(item, USAGE_FIELDS | {"id"}, "usage row", errors)
        if row is None:
            continue
        if not _text(row["id"]) or row["id"] in seen:
            errors.append("usage IDs must be nonempty and unique after export deduplication")
        else:
            seen.add(row["id"])
        if any(row[key] is not None and not _count(row[key]) for key in USAGE_FIELDS):
            errors.append("usage values must be nonnegative integers or null")
            continue
        for subset, parent in (("cached_input", "input"), ("reasoning", "output")):
            if row[subset] is not None and row[parent] is not None and row[subset] > row[parent]:
                errors.append(f"usage {subset} exceeds {parent}")
        valid_rows.append(row)
    if totals is None or len(valid_rows) != len(rows):
        return
    for key in USAGE_FIELDS:
        expected = (
            None if any(row[key] is None for row in valid_rows)
            else sum(row[key] for row in valid_rows)
        )
        if (
            totals[key] is not None and not _count(totals[key])
        ) or totals[key] != expected:
            errors.append(f"usage total {key} must reconcile; missing usage is null, not zero")


def _metrics(value: object, errors: list[str]) -> None:
    metrics = _object(
        value,
        {"logical_calls", "attempts", "outcomes", "request_attempts", "statistics", "usage", "savings"},
        "metrics", errors,
    )
    if metrics is None:
        return
    logical, attempts = metrics["logical_calls"], metrics["attempts"]
    if not _count(logical) or not _count(attempts):
        errors.append("logical_calls and attempts must be nonnegative integers")
        return
    if attempts < logical:
        errors.append("attempts must cover initiated logical calls at the same tool layer")
    if attempts and not logical:
        errors.append("known tool attempts require initiated logical calls in this complete population")
    outcomes = _object(
        metrics["outcomes"], {"succeeded", "failed", "cancelled", "unfinished"},
        "outcomes", errors,
    )
    if outcomes is not None:
        if not all(_count(count) for count in outcomes.values()) or sum(outcomes.values()) != attempts:
            errors.append("mutually exclusive outcomes must sum to attempts")
    samples = metrics["request_attempts"]
    stats = _object(
        metrics["statistics"], {"mean", "median", "p95", "percentile_method"},
        "statistics", errors,
    )
    if not isinstance(samples, list) or not samples or not all(_count(x) for x in samples):
        errors.append("request_attempts must contain nonnegative counts for completed requests")
    else:
        if sum(samples) != attempts:
            errors.append("disjoint completed-request rows must sum to inspected tool attempts")
        if stats is not None:
            expected = {
                "mean": statistics.mean(samples) if len(samples) >= 5 else None,
                "median": statistics.median(samples) if len(samples) >= 5 else None,
                "p95": sorted(samples)[math.ceil(0.95 * len(samples)) - 1]
                if len(samples) >= 20 else None,
            }
            for name, result in expected.items():
                if not _equal(stats[name], result):
                    errors.append(f"{name} must match completed-request samples and its minimum size")
            method = "nearest-rank" if len(samples) >= 20 else None
            if stats["percentile_method"] != method:
                errors.append("percentile_method must be nearest-rank at 20+ requests, otherwise null")
    savings = _object(
        metrics["savings"], {"unit", "baseline", "proposed", "combined_savings"}, "savings", errors,
    )
    if savings is not None:
        if savings["unit"] != "logical_tool_calls" or not all(
            _count(savings[key]) for key in ("baseline", "proposed", "combined_savings")
        ):
            errors.append("savings must use nonnegative same-unit logical tool counts")
        elif (
            savings["baseline"] != logical
            or savings["proposed"] > logical
            or savings["combined_savings"] != logical - savings["proposed"]
        ):
            errors.append("combined savings must reconcile without exceeding the logical baseline")
    _usage(metrics["usage"], errors)


def _impact(value: object, scope: object, errors: list[str]) -> None:
    if scope not in ("scenario", "workload"):
        errors.append("ranking_scope must be scenario or workload")
    if not isinstance(value, list):
        errors.append("impact must be an array")
        return
    seen = set()
    for item in value:
        row = _object(
            item,
            {"id", "scenario", "unit", "scenario_local", "branch_frequency",
             "frequency_evidence", "workload_weighted"},
            "impact row", errors,
        )
        if row is None:
            continue
        if not _text(row["id"]) or row["id"] in seen:
            errors.append("impact IDs must be nonempty and unique")
        else:
            seen.add(row["id"])
        if not _text(row["scenario"]) or row["unit"] not in ("tool_calls", "model_calls", "tokens"):
            errors.append("impact needs a scenario and a separate call/token unit")
        local, frequency = row["scenario_local"], row["branch_frequency"]
        if local is not None and not _number(local):
            errors.append("scenario-local impact must be nonnegative or null")
            continue
        if frequency is None:
            if scope == "workload" or row["frequency_evidence"] is not None:
                errors.append("workload ranking requires measured branch frequencies and evidence")
        elif not _number(frequency) or frequency > 1 or not _text(row["frequency_evidence"]):
            errors.append("branch frequency must be measured, cited and between zero and one")
            continue
        expected = None if local is None or frequency is None else local * frequency
        if not _equal(row["workload_weighted"], expected):
            errors.append("workload-weighted impact must reconcile; absent weights stay unknown")


def check_conformance(capture: object) -> list[str]:
    errors = []
    report = _object(
        capture,
        {"case", "response", "detailed_report", "executive_summary", "coverage",
         "metrics", "impact", "ranking_scope"},
        "capture", errors,
    )
    if report is None:
        return errors
    case = report["case"]
    if not isinstance(case, str) or case not in {*STOP_CASES, "completed-review"}:
        return ["unknown conformance case"]
    if not _text(report["response"]):
        errors.append("response must contain the exact captured Chat output")
    if case in STOP_CASES:
        reason, paths = STOP_CASES[case]
        response = report["response"]
        if not isinstance(response, str):
            return errors
        if not all(text in response for text in (reason, "Search scope:", "Paths checked:", *paths)):
            errors.append("stop response must identify the reason, search scope and checked paths")
        number = r"(?:\d+(?:\.\d+)?|zero|one|two|three|four|five|six|seven|eight|nine|ten)"
        unit = r"(?:(?:logical|tool|model|execution|downstream)\s+)*(?:calls?|attempts?|requests?)"
        if re.search(
            rf"\b(?:{number}\s+{unit}|{unit}(?:\s+counts?)?[\s\"'`*:=]+{number})\b",
            response.replace("_", " "), re.IGNORECASE,
        ):
            errors.append("stop response must not contain call counts")
        if re.search(
            r"(?im)^\s*(?:#{1,6}\s+|\*\*)(?:"
            + "|".join(re.escape(heading) for heading in (*SECTIONS, "Executive Summary"))
            + r")\b",
            response,
        ):
            errors.append("stopped audits must not embed report sections in Chat")
        if any(report[key] is not None for key in report if key not in {"case", "response"}):
            errors.append("stopped audits must not contain reports, counts, coverage or ranking data")
        return errors
    detailed, summary = report["detailed_report"], report["executive_summary"]
    if not _text(detailed):
        errors.append("completed review requires captured detailed Markdown")
    else:
        if _section_headings(detailed) != list(SECTIONS):
            errors.append("detailed report must contain the six ordered section headings")
    if not _text(summary):
        errors.append("completed review requires captured summary Markdown")
    else:
        rows, summary_errors = check_summary(summary)
        errors.extend(summary_errors)
        if isinstance(report["impact"], list) and len(rows) > len(report["impact"]):
            errors.append("summary priority rows must not exceed the supplied impact findings")
    _coverage(report["coverage"], errors)
    _metrics(report["metrics"], errors)
    _impact(report["impact"], report["ranking_scope"], errors)
    return errors


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path, help="captured conformance-case JSON envelope")
    args = parser.parse_args()
    try:
        capture = json.loads(
            args.capture.read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_object,
        )
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"Cannot read capture: {error}\n")
    errors = check_conformance(capture)
    if errors:
        print("\n".join(f"FAIL: {error}" for error in errors))
        return 1
    print("PASS: captured output matches the bounded review conformance checks.")
    print("Tool scope, artifact persistence and semantic correctness still require separate evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
