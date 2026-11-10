---
name: orchestration-efficiency-review
description: "Use when explicitly asked for quantitative retry, cache, fan-out or concurrency efficiency review: layered amplification, coalescing, deadline propagation, cancellation and critical-path versus off-path work. Analyze existing source and sanitized evidence without executing workloads."
disable-model-invocation: true
---

# Retry, cache and fan-out efficiency review

## Scope and permissions

Use only on an explicit request for this quantitative orchestration review.
Apply the active AI Efficiency & Performance Auditor's boundaries, evidence invariants,
six-section report and Executive Summary workflow. If inactive, read
`.github/agents/ai-efficiency-performance-auditor.agent.md` as guidance, not application
evidence; if unavailable, disclose it and request the methodology before claiming
a conforming audit.

Application source, configuration and evidence remain read-only.
Do not execute commands, invoke other agents, call external services, replay
workloads or add instrumentation. The only write exception is new Markdown
detailed audit and Executive Summary files under the core no-overwrite workflow.
Preserve sanitization gates and all audit-wide, scenario, guidance and per-file
budgets, including these skill reads. Recommend experiments; do not run them.
This skill does not silently enable service-performance or other optional modes.

Internal contract: `advisory-evidence/1`; report: `advisory-markdown/1`.
Reuse core scoped run/logical-operation/attempt/downstream IDs and safety
inventory; unknown correlation stays unknown, not guessed grouping.

## 1. Bind layers, ownership and dependency

Follow the named entry point through router/orchestrator, tool, SDK/transport,
cache, queue/provider and output consumer. Record
`Layer/path | Logical operation/attempt | Parent | Retry policy | Cache scope |
Fan-out/admission bound | Deadline/cancellation owner | Evidence/gap`.
Identify wrapper spans, attempt units, retry-versus-total settings, fallback,
provider quotas, deployment worker multiplicity and side-effect/error paths.
Do not multiply policies unless control flow establishes nested execution.

## 2. Use explicit metrics and denominators

| Metric | Definition and admissibility |
|---|---|
| Retry amplification | Attempts / initiated logical operations at one named layer; undefined ratio is N/A. Keep orchestration, tool and transport layers separate |
| Conditional retry bound | Product of total-attempt limits only on a proven nested branch; retries R means R+1 attempts only under the documented policy. Mutually exclusive fallbacks are separate branches |
| Fan-out width/depth | Direct child operations per parent and dependency-edge depth at a declared operation layer. Retries/chunks are not extra logical children; missing ancestry means bounds/unknown |
| Observed concurrency | Peak simultaneously active attempts from complete aligned start/end evidence with declared half-open intervals [start,end); asynchronous syntax or fan-out width alone is not measured concurrency |
| Cache hit rate | Valid usable hits / eligible lookups with complete hit/miss outcomes; expiry, invalidation, auth mismatch and errors are separate outcomes. Declare denominator and negative-cache rules; zero denominator is N/A |
| Coalescing candidates | Equivalent overlapping eligible reads under a complete single-flight key and compatible completion/error contract; follower count is not automatically avoidable attempts |
| Critical path | Longest dependency-connected elapsed path from complete causally linked timings; do not sum overlapping parent/child spans or parallel durations |
| Post-deadline work | Observed attempts/usage after a confirmed request deadline/disconnect, linked to cancellation ownership and consumer/cleanup obligations; necessary cleanup or durable jobs are not automatically waste |

Never infer system concurrency from a missing local semaphore. Queue wait,
backpressure, provider throttling, cache stampedes and off-path work require
their own evidence; a slow or off-critical-path operation may be necessary.
Timestamp skew, missing ends and sampled logs prevent exact overlap/critical
path claims. Report supplied aggregate definitions/coverage rather than running
code to compute large populations. Use core reconciliation and lower bounds.

## 3. Establish optimization applicability

Read reuse/coalescing needs a documented equivalence key, unchanged tenant,
identity/auth, policy, normalized input, freshness/invalidation and classification.
Model reuse also preserves prompt/context/model/settings, output schema and
required independent sampling. A cache hit need not eliminate all calls or cost.
Count actual avoided provider operations separately from lookup overhead.

Retries and suppression of writes require idempotency, outcome and uncertain-
completion evidence; failure/timeout alone does not mean the write did not happen.
Check retry budgets against the remaining deadline, backoff and cancellation
propagation. Do not cancel required cleanup, durable accepted jobs or work with
independent consumers merely because a client disconnected. Propose caps only
with known workload/provider/admission conditions; do not invent quotas.
Shared mechanisms across core/service findings are linked, not duplicated.

## 4. Report and validate

Use the six sections. Put layer/key/coverage limitations in Verdict, inventory
and safety eligibility in Call map, supported metrics in Runtime metrics, only
demonstrated avoidable work in Ranked findings, and conditional changes in
Proposed design. Separate scenario-local from measured-frequency traffic impact.
Keep call, token, latency, resource and cost units distinct and overlap counted once.

When useful, include separate baseline/proposed fenced Mermaid flows in Proposed
design: opaque IDs, sanitized operation classes, explicit layer/retry edges and
verified source/record citations in adjacent text. Unknown branches stay unknown.
Diagrams are not measured concurrency or proof of latency improvement. Do not
render externally, use image tools or include diagrams in the Executive Summary.
Apply core save/prevalidation/read-back/consent rules; do not create extra JSON.

Propose matched validation for transient/permanent failures, retry exhaustion,
concurrent identical reads, cache expiry/invalidation, differing identities,
uncertain writes, slow consumers, disconnects, deadline exhaustion and shutdown.
Preserve success, quality, freshness, ordering, error notifications, idempotency
and independent checks. Thresholds require stated requirements or approval;
measured comparative evidence is required before claiming improvement.
