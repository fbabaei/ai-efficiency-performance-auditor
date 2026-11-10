# Internal advisory evidence and comparison contract

Contract ID: `advisory-evidence/1`. Report ID: `advisory-markdown/1`.
These identify internal reasoning and Markdown fields, not a public JSON schema,
parser implementation or guarantee of deterministic model behavior. Keep the
core methodology version separately; record unknown parser/adapter versions.
Other optional review modes use the same core entities and counting invariants;
they need not load this reference unless performing comparison.

## Evidence entities

Represent only what inspected evidence establishes:

| Entity | Minimum fields when known |
|---|---|
| Audit/scenario | Side, scenario, revision, window/sample, methodology/contract, coverage, exclusions |
| Logical operation | Opaque operation/run/parent IDs, tool/model/embedding kind, purpose, identity/auth and freshness scope |
| Attempt | Scoped opaque ID, logical operation, layer, sequence, start/end/duration, outcome, retry/fallback link/reason |
| Downstream request | Opaque request/attempt link, service, read/write/side effects, idempotency, outcome |
| Usage | Attempt link, input/output/cached/reasoning, subset semantics, missingness, pricing source/date/currency/units |
| Consumption | Operation/result reference, known consumer or unused/unknown, source/record evidence |
| Finding | Mechanism, scenario, both-side citations, evidence level, confidence, local/traffic impact and denominators, overlap group, applicability, risk/effort, recommendation |

Use existing opaque identifiers only; never derive public hashes from sensitive
arguments or invent IDs to imply correlation. A local diagram label such as A
is presentation only. For missing IDs use the core's documented fallback rules,
lower bounds or unknowns. Keep ambiguous conflicting records, legitimate repeats
and partial usage visible. No object-key normalization, retry grouping or export
deduplication without the admissible contract.

Apply reconciliation to complete same-layer populations, not planned/unstarted
operations or nested layers. Outcome partitions and disjoint row sums must agree;
subset usage is not extra usage. Link savings overlap groups and use each
baseline operation once in combined savings. Reports do not establish that
overlap is absent merely because finding IDs differ.

## Applicability and decision

Carry the core safety inventory into every proposed optimization: tenant,
identity/auth, policy, freshness/invalidation, model/prompt/settings, output
schema, sampling/independent checks, read/write side effects and idempotency.
An unknown required condition prevents confirmed safe suppression/reuse.

All deltas require the same metric/unit and denominator on both sides.
Comparability can be metric-specific: comparable call rates do not make unlike
pricing, quality samples or latency percentiles comparable. Show excluded metrics
and why. Intentional changes must be identified, other conditions matched, and
quality/safety criteria satisfied before claiming overall validated improvement.
Zero baseline: N/A percentage. Missing value: unknown delta. Supplied point
estimates do not establish confidence intervals or causal improvement.

## Call-flow diagrams

Keep baseline and candidate/proposed graphs separate; never label a projection
as an observed candidate. Use opaque node IDs and sanitized operation classes,
annotating logical operations versus attempts, wrappers, retries and fan-out.
Cite verified nodes/edges in adjacent text. Unknown topology must be marked
unknown, not completed by inference. Graph width is not measured concurrency.
Critical paths require complete dependency/timing evidence, not summing nested
or parallel span durations. Omit a graph if evidence is insufficient.

Place optional fenced `mermaid` text only in the detailed Proposed design
section, never the Executive Summary. Escape labels; use no raw prompts,
arguments, retrieved text, links to external services or tool-execution directives.
Do not invoke renderers or broaden tools to produce a diagram.
