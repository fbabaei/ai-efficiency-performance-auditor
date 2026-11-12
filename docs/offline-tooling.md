# Offline companion tooling

These Python 3.10+ standard-library tools run only when a developer or separately
authorized CI runner invokes them. They do not collect telemetry, run application
workloads, execute benchmarks, call providers or grant execution to the auditor.
The [synthetic examples](../examples/offline/) are demonstrations, not measured
savings or recommended production thresholds.

Run commands from this repository root; no package installation is needed.

## Import already-sanitized OTLP JSON

```powershell
python -m auditor_tools import-otlp .\examples\offline\traces.json --confirm-sanitized --source-id capture-1 --output .\normalized-trace.json
```

`--confirm-sanitized` is mandatory before the tool opens the input. It confirms
the exact command-line input path, not sibling files. Sanitize upstream: the
importer is not a sanitizer or a scanner for secrets. It reads one UTF-8 OTLP
ExportTraceServiceRequest JSON object with `resourceSpans`, `scopeSpans` and
`spans`; not JSONL, gzip, protobuf, backend-specific envelopes or metrics/logs.
Unknown message fields are ignored. Duplicate JSON keys and non-finite numbers
are rejected, and input is bounded to 64 MiB.

The adapter follows [OTLP JSON encoding](https://opentelemetry.io/docs/specs/otlp/#json-protobuf-encoding):
hex trace/span IDs, integer status enums and decimal-string or integer nanosecond
timestamps. Nanoseconds are subtracted as integers before conversion to duration.
Missing/zero timestamps stay unknown. Malformed IDs, negative durations and
invalid selected usage fields are explicit errors.

The output contract is `auditor-traces/1`, adapter `otlp-json/1`:

| Output | Meaning |
|---|---|
| `source_id` | Caller-supplied non-sensitive identifier; default `input-1`, not an input path or payload hash |
| `coverage` | Always `unknown`; a complete-looking export is not proof of complete workload capture |
| `sanitization` | Input confirmation and output allowlist description, not independently verified privacy |
| `spans` | Trace/span/parent IDs, source-record coordinates, timestamps, duration, status, allowlisted operation and input/output tokens or null |
| `duplicates_removed` | Exact duplicate raw span records at the same trace/span identity; conflicting duplicate records are rejected |
| `limitations` | No logical-call, request-count, retry, task-success, pricing or complete-coverage inference |

Operation names are restricted to `chat`, `text_completion`, `generate_content`,
`embeddings`, `execute_tool`, `invoke_agent` and `create_agent`; other names become
`unknown`. Only `gen_ai.operation.name`, `gen_ai.usage.input_tokens` and
`gen_ai.usage.output_tokens` attributes are selected. Token fields require OTLP
`intValue`. Other conventions need an explicit future adapter update, not guessed
aliases. Resource attributes, span names/messages, arbitrary attributes, events,
links and payloads are never copied. IDs must themselves already be sanitized.

No automatic per-request rollup is performed: nested spans, wrappers, retries and
sampled exports make naive span/token summation unsafe. The importer provides
metadata evidence for review, not gate-ready measurements.

## Evaluate approved budgets

```powershell
python -m auditor_tools gate .\examples\offline\candidate.json --budgets .\examples\offline\budgets.json --baseline .\examples\offline\baseline.json --confirm-comparable --output .\gate-result.json
```

Both `--output` paths above use exclusive creation: existing files are never
overwritten, even on repeated runs. Parent directories must exist. Without
`--output`, JSON goes to stdout. A failed write is an error; any partial file
is left untouched and is not reported as successfully saved.

### Measurements: auditor-measurements/1

See [candidate](../examples/offline/candidate.json) and
[baseline](../examples/offline/baseline.json). The exact top-level fields are:
`schema`, `scenario`, `workload_id`, `quality_contract_id`, `conditions_id`,
`currency`, `coverage`, `requests`.

Use non-sensitive ASCII identifiers of at most 64 characters. `currency` names
the common cost currency; supply amounts consistently, never convert implicitly.
`coverage` is `complete`, `partial` or `unknown`. Each request has exactly:

| Field | Type and contract |
|---|---|
| `id` | Unique opaque identifier within the run |
| `success` | Boolean task outcome against the declared quality contract, or null; never inferred from span status |
| `latency_ms` | Nonnegative finite elapsed request duration, or null; not summed span duration |
| `tool_attempts`, `model_attempts` | Nonnegative integer attempts at separately declared layers, or null; include retries and failures, not nested duplicate wrappers |
| `input_tokens`, `output_tokens` | Nonnegative integer usage across a reconciled request population, or null; no duplicated cache/reasoning subsets |
| `cost` | Nonnegative finite request cost including failed attempts in the stated currency, or null |

Include successes, failures, timeouts and cancellations in the initiated-request
population. Use null for incomplete usage/outcomes; never fabricate a zero.
An exporter/human must establish these semantics: the runner cannot verify
sampling, attribution, pricing, quality grading or missing requests.

Use the workload ID for task/input distribution, quality-contract ID for
approved output criteria, and conditions ID for identity/policy, data versions,
cache warmness, provider, concurrency and measurement settings. IDs are
attestations, not content hashes or independent proof of matched conditions.
Record intentional candidate changes separately in your experiment documentation.

### Policy: auditor-budgets/1

The exact fields are `schema`, `approved`, `scenario`, `quality_contract_id`,
`currency`, `limits`. [Example policy](../examples/offline/budgets.json) approval
is synthetic only. Replace it with actual approved requirements; the tool
requires `approved: true` and a `success_rate` minimum.

Each unique metric has one or more `min`, `max`, `max_relative_increase` rules.
Thresholds are finite nonnegative numbers; success-rate bounds are in [0,1].
Relative caps are fractional increases: `0.1` allows 10 percent. A decrease is
negative and satisfies an increase cap. Success rate uses an absolute minimum,
not a relative-increase rule. Crossing an absolute bound fails; equality passes.

| Metric | Unit and denominator | Availability |
|---|---|---|
| `success_rate` | Successful tasks / all supplied initiated requests | All task outcomes known; at least one request |
| `latency_mean_ms` | Mean elapsed milliseconds / request | All durations known; at least five requests |
| `latency_p95_ms` | Nearest-rank elapsed milliseconds; rank ceil(0.95*n) | All durations known; at least twenty requests |
| `tool_attempts_per_request`, `model_attempts_per_request` | Attempts / all requests | Complete values at one declared layer per metric |
| `input_tokens_per_request`, `output_tokens_per_request` | Tokens / all requests | Complete reconciled values |
| `cost_per_request` | Stated currency / all requests | Complete request costs |
| `cost_per_successful_task` | Total cost including failed requests / successful tasks | All costs and outcomes known; nonzero successes |

Complete coverage is required for decisive gate checks. Relative rules also need
a complete baseline, equal scenario/workload/quality/conditions/currency IDs and
`--confirm-comparable`. Unknown or zero baseline makes a relative check
inconclusive. Absolute candidate checks can still be evaluated without a
baseline. Different sample counts are permitted for comparable per-request rates;
point comparisons do not establish significance or non-inferiority.

### Results and CI

`auditor-gate/1` returns the status, scenario, currency, coverage, sample size,
derived metrics and each check's threshold, candidate/baseline value, observed
quantity, status and reason. Missing metrics are JSON null. Exit codes:

| Code | Meaning |
|---|---|
| 0 | All approved checks pass |
| 1 | At least one supported check fails; other inconclusive checks remain visible |
| 2 | Invalid/unapproved input, unsupported schema, read/write/encoding error or output collision |
| 3 | No failed check, but at least one check is inconclusive |

In CI, propagate the command's exit code unchanged; do not turn code 3 into a
pass or ignore quality failures because cost decreased. No CI workflow or remote
integration is installed. Approval/completeness/comparability are caller claims,
and passing gates is neither finding resolution nor a causal quality-preserving
improvement claim.

## Hand artifacts back to the auditor

Explicitly request `efficiency-budget-review` with exact policy/result paths.
Confirm exact-path sanitization in Chat before runtime artifact access unless
an independently trusted payload-free metadata boundary is available. The tool's
output marker alone does not override the agent's sanitization rules.
The auditor interprets results; it never runs the importer or gate.

For missing telemetry request `measurement-readiness`. For finding-level status,
explicitly request verification through `audit-comparison`, supplying both-side
evidence and approved quality/safety results.
