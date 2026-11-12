---
name: measurement-readiness
description: "Use when explicitly asked to identify missing telemetry or plan measurement for AI efficiency findings. Propose payload-free instrumentation and representative validation without collecting data, modifying code or running workloads."
disable-model-invocation: true
---

# Measurement-readiness review

## Scope and permissions

Use only on an explicit measurement-readiness request. Apply the active
AI Efficiency & Performance Auditor's boundaries, evidence invariants,
six-section report and Executive Summary workflow. If inactive, read
`.github/agents/ai-efficiency-performance-auditor.agent.md`
as guidance, not application evidence; if unavailable, disclose it and request
the methodology before claiming a conforming audit.

Application source, configuration, reports and traces remain read-only.
Do not execute commands, install instrumentation, collect telemetry, invoke other
agents, call external services or run workloads. The only write exception is new
Markdown detailed audit and Executive Summary files under the core no-overwrite
workflow. Preserve sanitization gates and all audit-wide, scenario, guidance and
per-file budgets, including these skill reads. Load other modes only when
explicitly requested; share evidence, budget and one report pair.

## 1. Bind the question and current coverage

Use the named scenario/entry point, current audit findings, or exact supplied
reports. Supplied-report-only requests skip application discovery, source and
trace inspection; preserve "From supplied report; not reverified" for locations.
Missing sites stay unknown, never invented as instrumentation locations.
Distinguish unavailable instrumentation, sampled/partial exports, unknown
correlation and uninspected source; absence of telemetry does not prove a defect.

For each claim specify the decision it would support: avoiding work, counting
attempts, measuring elapsed latency/cost, or preserving quality and reliability.
Inventory currently observed fields and missingness without collecting new data.

## 2. Propose the smallest payload-free measurement

Use `Finding/scenario | Decision | Existing evidence | Missing fields |
Proposed source site or unknown | Population/unit | Privacy safeguards |
Acceptance and owner decision`.

Recommend only necessary metadata:
- Opaque request, logical-operation, attempt and parent IDs; explicit retry layer,
  sequence, wrapper/attempt role and complete terminal outcomes.
- Aligned start/end or monotonic duration, queue/deadline/cancellation ownership;
  include failed/timed-out/cancelled attempts and known missing exports.
- Provider-recorded input/output token usage and subset semantics; applicable
  currency and pricing provenance. Characters are not tokens.
- Explicit cache eligibility and usable hit/miss outcomes, version/freshness and
  equivalent identity scope, without tenant names or sensitive cache keys.
- Result-consumption metadata and task-success/quality outcomes against an
  approved contract. Span status is not task success.

Never recommend logging raw prompts, arguments, retrieved content, credentials,
customer identifiers or full responses. Do not hash sensitive payloads as a
privacy shortcut. Propose existing opaque IDs, access restrictions, retention
and cardinality limits; mark policy approvals unknown rather than inventing them.
Instrumentation overhead, sampling bias and clock skew require explicit review.

## 3. Define readiness and a validation handoff

Classify each decision as ready, partial or blocked, citing its exact missing
field, population, contract or approval. A complete schema alone does not make
evidence representative, correlated or quality-preserving.
Specify unit/denominator, completion/failure coverage, representative workload,
repetitions and uncertainty; propose thresholds for approval, not as requirements.
Follow core sample minima: mean/median need five requests; p95 needs twenty.
Cost per successful task includes costs of failed requests; zero successes or
missing cost/outcomes makes that metric unknown, not zero.

Keep instrumentation gaps and proposals in Validation plan and missing evidence;
only independently demonstrated waste enters Ranked findings. Retain the six
sections and summary limits. The offline companion can import already-sanitized
OTLP JSON or check supplied measurements, but the auditor never runs it.
Do not imply that OTLP alone establishes logical calls, complete workloads,
safe reuse, task success or measured savings.
