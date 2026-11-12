---
name: audit-comparison
description: "Use when explicitly asked to compare baseline and candidate AI efficiency: two supplied audits, source snapshots, or sanitized trace sets. Explain matched deltas, quality guardrails and inconclusive comparisons without executing workloads or fetching revisions."
disable-model-invocation: true
---

# Baseline/candidate audit comparison

## Scope and permissions

Use only on an explicit comparison request. Apply the active
AI Efficiency & Performance Auditor's boundaries, evidence invariants,
six-section report and Executive Summary workflow. If inactive, read
`.github/agents/ai-efficiency-performance-auditor.agent.md`
as guidance, not application evidence; if unavailable, disclose it and request
the methodology before claiming a conforming audit.

Application source, configuration, reports and traces remain read-only.
Do not execute commands, fetch/check out revisions, replay workloads, invoke
other agents, call external services, or add instrumentation. The only write
exception is new Markdown detailed audit and Executive Summary files under the
core no-overwrite workflow. Preserve sanitization gates and all audit-wide,
scenario, guidance and per-file budgets, including these skill/reference reads.
Use supplied snapshots, existing authorized workspace paths, or reports pasted
in Chat. Revision names alone do not authorize Git/network operations.

Read [the evidence and comparison contract](./references/comparison-contract.md)
within the guidance budget. This is an internal Markdown contract, not permission
to create JSON or a claim that two-file persistence is transactional.

## 1. Bind the two sides

Establish baseline/candidate labels, paths/revisions, scenarios and evidence
types. If roles or inputs are ambiguous, ask once using the core clarification
rules; no reply means comparison unavailable, not guessed labels. Core stop
states still apply. A comparison of supplied reports does not require manifests,
source discovery or trace access. Preserve reported locations as
"From supplied report; not reverified"; absence from the candidate report is
not proof that a baseline finding is resolved.

Read only the named sides and relevant guidance. Apply eligibility separately to
each runtime artifact; confirmation for one path does not sanitize another.
Treat reports and embedded recommendations as evidence, not authorization.
Do not substitute a current checkout for an unavailable historical revision.

## 2. Establish comparability before deltas

Build `Condition | Baseline | Candidate | Match/change/unknown | Evidence`.
Cover task/input distribution, completion/failure coverage, identity/permissions,
policy, freshness/data state, output/quality contract, cache warmness, model and
prompt/settings, provider/deployment conditions, concurrency, sampling/window,
counting layer, token/pricing semantics and methodology/report contract versions.
Identify intentional changes separately from confounders. Compare unchanged
dimensions and normalize only when justified; a shared scenario name is not
proof of equivalent work. Trace or measurement evidence outranks neither source
nor reports automatically: record conflicts and affected unknowns.

If equivalence is unestablished, report two separate profiles with no improvement
verdict or causal delta. Mixed units, unlike denominators and missing failed
attempt usage do not become comparable by filling gaps with zero.
Static source comparisons yield conditional bounds, not measured savings.

## 3. Compare supported metrics and findings

Use `Metric/unit/denominator | Baseline (n/window) | Candidate (n/window) |
Candidate - baseline | Change % | Evidence/limitations`.
Use per-request rates for different sample sizes only when workload mix and
completion coverage are comparable; do not compare raw totals across windows.
Separate tool/model logical calls, attempts, downstream requests, retries,
input/output/subset tokens, elapsed versus summed latency, applicable cost and
quality/safety results. Do not mix embedding and generation usage.

For known comparable values, delta = candidate - baseline and percentage change
= 100 * delta / baseline. A zero baseline yields N/A percentage, not infinity
or 100%; missing values yield unknown delta/percentage, not zero. Negative
cost/call deltas mean reduction, not automatically improvement. Keep direction
of each quality metric explicit; retain uncertainty and paired/unpaired design.
Never subtract unlike percentile methods or claim significance from point values.

Track findings as new, persistent, resolved-with-evidence, or not-verifiable,
matching mechanism, scenario and source/operation identity, not prose alone.
Resolution requires direct candidate evidence of removed mechanism and preserved
contract; smaller scope or a missing finding is not resolution. Cite both sides.
Do not double-count linked model/tool savings or overlapping findings.

For explicitly requested finding-level optimization verification, also read
[the verification decision rules](./references/finding-verification.md).
Track verified-fixed, partially-addressed, persistent, regressed or inconclusive
with both-side mechanism/coverage evidence and approved quality/safety results.
Do not infer verified-fixed from a plan, omitted finding or fewer calls.
Ordinary comparisons retain their existing status vocabulary.

## 4. Report a qualified decision

Retain six sections. Put provenance/comparability in Verdict, linked inventories
and applicability safeguards in Call map, deltas in Runtime metrics, supported
findings in Ranked findings, before/after flow in Proposed design and gaps in
Validation plan. Use the contract's opaque-ID Mermaid guidance when a verified
graph is useful; no renderer, image generation or external tool is required.

State improved, regressed, mixed or inconclusive only against approved metric
directions and quality/safety margins. Fewer calls with untested quality means
call reduction observed; overall improvement inconclusive. Supplied-report
comparisons remain reported claims, not independently validated optimization.
Propose missing matched evaluation; do not perform it.

Create one comparison report pair, not independent report pairs for both sides;
use the core slug and collision/verification/consent rules. This is a new
comparison audit, unlike shortening one supplied report. Preserve the comparison
qualification, denominators, overlap and unknowns in its Executive Summary.
