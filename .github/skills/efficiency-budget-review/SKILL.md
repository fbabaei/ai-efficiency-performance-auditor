---
name: efficiency-budget-review
description: "Use when explicitly asked to interpret supplied offline efficiency gate results and approved budgets. Explain pass, fail or inconclusive outcomes, quality guardrails and evidence gaps without running the companion tools or enforcing CI."
disable-model-invocation: true
---

# Efficiency-budget result interpretation

## Scope and permissions

Use only on an explicit efficiency-budget-review request. Apply the active
AI Efficiency & Performance Auditor's boundaries, evidence invariants,
six-section report and Executive Summary workflow. If inactive, read
`.github/agents/ai-efficiency-performance-auditor.agent.md`
as guidance, not application evidence; if unavailable, disclose it and request
the methodology before claiming a conforming audit.

Application code, measurements, policies and gate results remain read-only.
Do not execute commands, enforce CI, collect telemetry, invoke other agents,
call external services or run benchmarks. The only write exception is new
Markdown detailed audit and Executive Summary files under the core no-overwrite
workflow. Preserve sanitization gates and all audit-wide, scenario, guidance and
per-file budgets, including these skill reads. Do not load other skills unless
explicitly requested; share one evidence budget and one report pair.

## 1. Bind named results and approved requirements

Read only the user-named gate result and budget policy, plus supplied measurements
when explicitly in scope. This is report interpretation, not application
discovery or permission to inspect referenced source/traces. Apply runtime
sanitization gates before any measurement/artifact payload access.
Check the declared schema versions, scenario, currency, sample size, coverage,
approved quality contract and each rule's units, direction and threshold.
Missing approval means proposed thresholds, not accepted requirements.
Missing policy or input prevents independent confirmation of the gate verdict.

The offline contracts are auditor-measurements/1, auditor-budgets/1 and
auditor-gate/1; trace import separately uses auditor-traces/1 and otlp-json/1.
These are not the core advisory evidence/report contracts or historical checker
envelopes. Unknown schema versions require disclosure, not guessed fields.

## 2. Explain the decision and its limits

Use `Metric/unit | Approved rule | Candidate | Baseline | Check status |
Evidence and limitation`. Preserve pass, fail and inconclusive separately.
An exit code or a supplied PASS line is not independent proof of correct inputs.
A failure dominates an overall inconclusive result only when its check is
itself supported; preserve the remaining unknown checks.

Missing usage, zero successful tasks, incomplete coverage, insufficient sample
size, absent comparable baseline or zero baseline for relative changes must not
be converted to zeros or passes. Baseline matching identifiers and explicit
comparability confirmation are user attestations, not a causal experiment.
Never infer task success from span status or quality from reduced cost.
Cost per successful task includes failed-request costs; unlike currencies,
units, populations and quality contracts are not comparable.

An approved success-rate minimum is required by the offline gate. It does not
prove full safety or quality equivalence. Passing budgets is not finding
resolution, statistical significance or overall validated improvement.
Budget violations are observations, not proof of safely avoidable work.

## 3. Report without enforcing

Retain the six sections: supplied provenance in Verdict, only established
inventories, supported metrics/rules in Runtime metrics, independently supported
mechanisms in Ranked findings, proposed corrections in Proposed design and
missing inputs/repeated evaluation in Validation plan and missing evidence.
Keep unproven causes unranked and the existing summary table/limits.
Use core create-once/read-back/preview consent. No CI configuration, policy
edits, JSON files or gate execution; those require separately authorized tooling.
