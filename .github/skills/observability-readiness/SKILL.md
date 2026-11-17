---
name: observability-readiness
description: "Use when explicitly asked to assess observability readiness for AI efficiency audits. Review telemetry coverage and metadata gaps from code, config or sanitized exports without collecting data, modifying code or running workloads."
disable-model-invocation: true
---

# Observability-readiness review

## Scope and permissions

Use only on an explicit observability-readiness request. Apply the active
AI Efficiency & Performance Auditor boundaries, evidence invariants,
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

## 1. Bind observability to decisions

Start from one named scenario/entry point and map each efficiency question to
required observability evidence: retries, latency, token usage, cache behavior,
failures and task outcomes. Supplied-report-only requests skip discovery/source
inspection and preserve "From supplied report; not reverified" for locations.
Missing locations remain unknown, never invented as instrumentation sites.

Distinguish telemetry absence from demonstrated defects. Missing dashboards or
alerts do not prove waste; they block confidence and verification readiness.

## 2. Check minimum telemetry contracts

Use `Decision | Existing evidence | Missing telemetry | Source site or unknown |
Population/unit | Privacy safeguards | Validation owner`.

Require payload-free metadata only:
- Opaque request, operation, attempt and parent identifiers; explicit retry layer
  and terminal outcomes (success, failure, timeout, cancellation).
- Start/end timing or monotonic duration with queue/deadline/cancellation
  context; include failed and timed-out attempts.
- Provider-recorded token usage semantics and pricing provenance when cost
  decisions are requested. Characters are not tokens.
- Cache-eligibility and usable hit/miss outcomes with identity/freshness scope,
  without tenant names or sensitive keys.
- Task-quality outcomes tied to an approved contract. Span status is not task success.

Never recommend logging raw prompts, retrieved content, credentials, customer
identifiers or full responses. Do not hash sensitive payloads as a shortcut.
Require retention/cardinality controls and approval boundaries; mark unknown
approvals explicitly.

## 3. Define readiness and handoff

Classify each decision as ready, partial or blocked, citing exact missing fields,
population coverage, approval dependencies or quality-contract gaps. Keep
instrumentation gaps and monitoring proposals in Validation plan and missing
evidence; only independently demonstrated mechanisms belong in Ranked findings.

Call out observability quality risks: sampling blind spots, clock skew,
high-cardinality labels, missing correlation and alert-noise tradeoffs.
State unknowns explicitly rather than inferring clean coverage.

Do not build dashboards, deploy alert rules, edit code or run tooling.
The offline companion can import already-sanitized OTLP JSON and evaluate
supplied budget inputs, but the auditor never runs it.
