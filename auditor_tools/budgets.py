"""Deterministic gates over supplied per-request measurements, not benchmarks."""

from decimal import Decimal
import math

from auditor_tools.contracts import identifier, integer, mapping, number, sequence


REQUEST_FIELDS = {
    "id", "success", "latency_ms", "tool_attempts", "model_attempts",
    "input_tokens", "output_tokens", "cost",
}
CONDITIONS = ("scenario", "workload_id", "quality_contract_id", "conditions_id", "currency")
METRICS = {
    "success_rate", "latency_mean_ms", "latency_p95_ms",
    "tool_attempts_per_request", "model_attempts_per_request",
    "input_tokens_per_request", "output_tokens_per_request",
    "cost_per_request", "cost_per_successful_task",
}


def _finite_result(value: Decimal) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("aggregated metric exceeds the supported numeric range")
    return result


def _measurements(payload: object) -> tuple[dict[str, object], dict[str, float | None]]:
    run = mapping(payload, "measurements")
    if set(run) != {"schema", *CONDITIONS, "coverage", "requests"}:
        raise ValueError("measurements fields must match auditor-measurements/1")
    if run["schema"] != "auditor-measurements/1":
        raise ValueError("unsupported measurements schema")
    for field in CONDITIONS:
        identifier(run[field], field)
    if run["coverage"] not in ("complete", "partial", "unknown"):
        raise ValueError("coverage must be complete, partial or unknown")
    raw_requests = sequence(run["requests"], "requests")
    requests: list[dict[str, object]] = []
    ids: set[str] = set()
    for item in raw_requests:
        request = mapping(item, "request")
        if set(request) != REQUEST_FIELDS:
            raise ValueError("request fields must match the per-request contract")
        request_id = identifier(request["id"], "request id")
        if request_id in ids:
            raise ValueError("duplicate request id")
        ids.add(request_id)
        if request["success"] is not None and type(request["success"]) is not bool:
            raise ValueError("success must be true, false or null")
        for field in REQUEST_FIELDS - {"id", "success"}:
            value = request[field]
            if value is not None:
                if field in {"tool_attempts", "model_attempts", "input_tokens", "output_tokens"}:
                    integer(value, field)
                else:
                    number(value, field)
        requests.append(request)
    metrics: dict[str, float | None] = {field: None for field in METRICS}
    count = len(requests)
    if not count:
        return run, metrics
    successes = (
        sum(request["success"] is True for request in requests)
        if all(request["success"] is not None for request in requests) else None
    )
    if successes is not None:
        metrics["success_rate"] = successes / count
    for field, metric in (
        ("tool_attempts", "tool_attempts_per_request"),
        ("model_attempts", "model_attempts_per_request"),
        ("input_tokens", "input_tokens_per_request"),
        ("output_tokens", "output_tokens_per_request"),
        ("cost", "cost_per_request"),
    ):
        if all(request[field] is not None for request in requests):
            total = sum(
                (Decimal(str(number(request[field], field))) for request in requests), Decimal(0),
            )
            metrics[metric] = _finite_result(total / count)
            if field == "cost" and successes:
                metrics["cost_per_successful_task"] = _finite_result(total / successes)
    if all(request["latency_ms"] is not None for request in requests):
        durations = sorted(number(request["latency_ms"], "latency_ms") for request in requests)
        if count >= 5:
            metrics["latency_mean_ms"] = _finite_result(
                sum((Decimal(str(value)) for value in durations), Decimal(0)) / count,
            )
        if count >= 20:
            metrics["latency_p95_ms"] = durations[math.ceil(0.95 * count) - 1]
    return run, metrics


def evaluate_budgets(
    candidate: object, policy: object, baseline: object = None, *, comparable: bool = False,
) -> dict[str, object]:
    rules = mapping(policy, "budgets")
    if (
        set(rules) != {
            "schema", "approved", "scenario", "quality_contract_id", "currency", "limits",
        }
        or rules.get("schema") != "auditor-budgets/1"
        or rules.get("approved") is not True
    ):
        raise ValueError("budgets must match auditor-budgets/1 and be explicitly approved")
    run, metrics = _measurements(candidate)
    for field in ("scenario", "quality_contract_id", "currency"):
        if identifier(rules[field], field) != run[field]:
            raise ValueError(f"budget and candidate {field} must match")
    previous: dict[str, object] | None = None
    baseline_metrics: dict[str, float | None] = {}
    if baseline is not None:
        previous, baseline_metrics = _measurements(baseline)
    limits = sequence(rules["limits"], "limits")
    validated: list[dict[str, object]] = []
    seen: set[str] = set()
    for item in limits:
        rule = mapping(item, "limit")
        metric = rule.get("metric")
        if not isinstance(metric, str) or metric not in METRICS or metric in seen:
            raise ValueError("limits must name unique supported metrics")
        seen.add(metric)
        fields = set(rule) - {"metric"}
        if not fields or not fields <= {"min", "max", "max_relative_increase"}:
            raise ValueError("limit requires min, max or max_relative_increase")
        for field in fields:
            threshold = number(rule[field], "threshold")
            if metric == "success_rate" and field in {"min", "max"} and threshold > 1:
                raise ValueError("success-rate thresholds must be between zero and one")
        if "min" in rule and "max" in rule and number(rule["min"], "min") > number(rule["max"], "max"):
            raise ValueError("minimum threshold exceeds maximum")
        if metric == "success_rate" and "max_relative_increase" in rule:
            raise ValueError("success_rate uses an absolute minimum, not a relative increase cap")
        validated.append(rule)
    if not any(rule["metric"] == "success_rate" and "min" in rule for rule in validated):
        raise ValueError("an approved success_rate minimum is required")
    comparisons_match = (
        previous is not None and comparable
        and previous["coverage"] == "complete"
        and all(previous[field] == run[field] for field in CONDITIONS)
    )
    checks: list[dict[str, object]] = []
    for rule in validated:
        metric = str(rule["metric"])
        value = metrics[metric]
        for field in sorted(set(rule) - {"metric"}):
            threshold = number(rule[field], "threshold")
            reason = ""
            observed = value
            if run["coverage"] != "complete":
                reason = "candidate coverage is not complete"
            elif value is None:
                reason = "missing values, zero denominator or insufficient sample size"
            elif field == "max_relative_increase":
                base = baseline_metrics.get(metric)
                if not comparisons_match:
                    reason = "matched complete baseline and explicit comparability confirmation required"
                elif base is None or base == 0:
                    reason = "baseline metric is unknown or zero; relative change is undefined"
                else:
                    observed = _finite_result(
                        (Decimal(str(value)) - Decimal(str(base))) / Decimal(str(base)),
                    )
            status = "inconclusive"
            if not reason and observed is not None:
                breached = observed < threshold if field == "min" else observed > threshold
                status = "fail" if breached else "pass"
                reason = "approved threshold breached" if breached else "approved threshold satisfied"
            checks.append({
                "metric": metric, "rule": field, "threshold": threshold,
                "candidate": value, "baseline": baseline_metrics.get(metric),
                "observed": observed, "status": status, "reason": reason,
            })
    statuses = {check["status"] for check in checks}
    overall = "fail" if "fail" in statuses else "inconclusive" if "inconclusive" in statuses else "pass"
    return {
        "schema": "auditor-gate/1", "status": overall, "scenario": run["scenario"],
        "coverage": run["coverage"], "currency": run["currency"],
        "workload_id": run["workload_id"], "quality_contract_id": run["quality_contract_id"],
        "conditions_id": run["conditions_id"],
        "comparability_confirmed": comparable, "comparison_conditions_match": comparisons_match,
        "sample_size": len(sequence(run["requests"], "requests")),
        "metrics": metrics, "checks": checks,
        "limitations": [
            "Input completeness, quality outcomes and matching conditions are user attestations.",
            "A gate pass is not statistical significance, verified finding resolution or causal improvement.",
            "All supplied outcomes are included; null is unknown, not zero.",
        ],
    }
