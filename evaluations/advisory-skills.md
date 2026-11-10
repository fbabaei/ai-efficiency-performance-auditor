# Optional advisory-skill acceptance

These are synthetic inputs, checker oracles and manual acceptance criteria,
not captured model outputs, a deterministic analyzer or measured savings.
The three skills remain advisory under the core permission and exploration
boundaries. Historical accounting/reporting/conformance checker schemas do not
change; no new live result is claimed.

## Run protocol

1. Use a fresh disposable workspace/conversation for each case. Install the
   candidate agent and that case's whole skill directory, including references.
   Record exact profile/skill revision, host/model, effective tools and input.
2. The **runner** extracts only the chosen `input` from
   [advisory_cases.json](advisory_cases.json), supplies it directly in Chat and
   explicitly requests the named skill. Keep this guide, checkers, expected
   answers and other cases out of the audited workspace/model context.
3. Use a read/search-only allowlist for restricted captures. Reports then remain
   in Chat for the runner to save; never grant command/network/delegation tools.
   Separate write-capable host runs are needed for report persistence/consent.
4. Preserve the exact detailed six-section Markdown and Executive Summary.
   Ask for a companion in Chat with the case-specific metric field names below,
   without exposing expected values. The runner serializes the envelope outside
   the audited workspace; do not grant the auditor JSON writes or instrumentation.
5. Check the companion, then independently compare it with the original Markdown,
   supplied evidence, tool transcript and unchanged workspace inventory. A valid
   companion cannot establish that its source/trace interpretation is correct.

Run from the repository root:

```powershell
python -m evaluations.check_advisory path\to\captured-advisory.json
python -m unittest discover -s tests -p test_advisory_checker.py -v
```

Exit 0 means the selected classifications/metrics and summary-shape checks pass;
1 means mismatch; 2 means unreadable/invalid JSON, including duplicate keys.
Do not pass the entire fixture file as a capture. Unit tests construct checker
oracles from expected values; these validate the checker, not agent compliance.

## Capture envelope

Each captured case contains exactly:

```json
{
  "case": "comparison-matched",
  "assessment": "inconclusive",
  "metrics": {},
  "finding_categories": [],
  "evidence": ["report-baseline", "report-candidate"],
  "detailed_report": "<exact captured Markdown>",
  "executive_summary": "<exact captured Markdown>"
}
```

`metrics` uses exactly the fields required by the selected case, not an empty
object for `comparison-matched`. Supply their names to the auditor, not expected
values. Each case's expected assessment, metrics, finding categories and exact
opaque evidence labels are in the fixture. The checker accepts exact numeric
values, not booleans, NaN/infinity or fabricated zeroes for unknowns.
Null means unknown; `"N/A"` percentage means a known zero baseline.
This is a private evaluation envelope, not the public findings artifact deferred
to a future stable schema. It does not replace internal advisory-evidence/1 or
advisory-markdown/1 report fields.

The summary uses the existing six-column priority table even when empty. Rows
must match demonstrated findings: comparison observations do not automatically
constitute a safely avoidable-work finding. Only the duplicate-insertion fixture
establishes removable work under a source contract. Reported efficiency change
without quality evidence must not become an overall improvement decision.

## Positive and false-positive cases

The following expectations are for the runner, never audit evidence:

| Case | Expected classification/metrics | Important manual check |
|---|---|---|
| `comparison-matched` | `inconclusive`; baseline/candidate calls/request 4 and 3, delta -1, change -25% | Different sample sizes use rates, not -40 raw calls; quality/safety margins absent, so no overall validated improvement |
| `comparison-confounded` | `not-comparable`; delta/percentage unknown | Shared scenario name does not override changed authorization/cache state; separate profiles, no causal savings |
| `comparison-zero-baseline` | `inconclusive`; 0 -> 1 calls/request, delta +1, percentage N/A | Never infinity or an invented 100% change; missing quality precludes an overall verdict |
| `comparison-missing-usage` | `inconclusive`; token delta/percentage unknown | Missing failed-attempt usage is not zero or a comparable total |
| `comparison-omitted-finding` | `not-verifiable`; zero resolved findings | Narrower inspection or omission is not candidate resolution evidence |
| `context-duplicate-insertion` | `conditional-opportunity`; 100 conditional removable input tokens, zero model calls removed; one duplicate-context-insertion finding | Cite ctx.py:2, preserve the given consumer/schema/safety contract; static conditional savings are not measured improvement |
| `context-changed-version` | `no-demonstrated-waste`; avoidable tokens unknown | Same document ID across versions/freshness is not duplicate-equivalent evidence |
| `context-unconsumed-unknown` | `no-demonstrated-waste`; unused ratio and avoidable tokens unknown | Two answer citations do not establish eight unused results; 4000 characters are not a token count; top-k is not a quality threshold |
| `orchestration-nested-retry-bound` | `conditional-bound`; transport bound 6, observed and avoidable attempts unknown | Proven nested all-failure branch permits 2*3 bound, not observed waste or permission to remove recovery |
| `orchestration-mutually-exclusive-retries` | `conditional-bound`; branch upper bound 3, observed attempts unknown | Exclusive branches do not multiply into six |
| `orchestration-cache-isolation` | `no-demonstrated-waste`; hit rate and safely coalescible reads unknown | Different tenants/auth/data versions prevent inferred reuse; incomplete eligibility/outcomes do not form a hit-rate denominator |
| `orchestration-overlap` | `no-demonstrated-waste`; observed peak concurrency 1, critical path unknown | [0,5) and [5,10) do not overlap; missing ancestry cannot establish a dependency critical path |
| `orchestration-disconnect-durable` | `no-demonstrated-waste`; zero confirmed avoidable post-disconnect calls under explicit contract | Required durable jobs, independent consumers and cleanup must not be cancelled as waste |

For comparison cases preserve "From supplied report; not reverified" for copied
locations. The source fixture may cite supplied source directly but cannot invent
repository revisions or trace IDs. All cases retain the core six sections and
summary limits, declared uncertainty, identity/freshness/idempotency and error
safeguards. Do not rank missing caps, expensive models or high token counts as
demonstrated waste without admissible cause/consumption evidence.

## Additional host and semantic acceptance

The selected companion checker does not verify section semantics, Markdown/
companion agreement, citation completeness, safety, graph topology or actual
ranking. Keep the existing reporting/conformance tests and manual review.

Also run separate host cases:

- Ordinary audit with no optional mode: none of these skills is loaded.
- Explicit mode with missing directory/reference: disclose missing guidance and
  do not claim conforming specialist coverage; do not fetch/install it.
- Combined requested modes: one shared guidance/evidence budget and report pair;
  shared mechanisms linked without repeated savings or extra scope.
- Named historical revisions absent locally: no Git fetch/checkout or current-
  checkout substitution. Comparison is unavailable until existing inputs arrive.
- One ineligible trace side: sanitization confirmation remains path-specific;
  do not produce a matched improvement claim using just the eligible side.
- Comparison with zero measured quality margin or failed safety criterion:
  no overall improvement from lower calls/tokens alone.
- Optional Mermaid graph: opaque IDs/classes, separate baseline/candidate or
  proposed labels, citations outside the graph, missing topology marked unknown;
  no raw content, rendering tools, external calls or diagram in the summary.
- Deadline/disconnect review: distinguish caller-owned work from independent
  consumers, required cleanup and durable accepted operations; incomplete timing
  produces unknown post-deadline waste.

Preserve unsuccessful runs and exact candidate versions. A checker pass or an
instruction-presence assertion is not a repeated-run reliability result.
