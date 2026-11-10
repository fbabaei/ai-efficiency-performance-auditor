# AI Efficiency & Performance Auditor

**Developer and author:** Fereydoun Babaei.

The [AI Efficiency & Performance Auditor](../.github/agents/ai-efficiency-performance-auditor.agent.md)
is a reviewer with read-only application access and report-only file creation.
It examines source code and existing
sanitized traces to answer:

> Which tool and model calls are avoidable, where might tokens or model capacity
> be wasted, and how can we improve efficiency without weakening correctness,
> security, or reliability?

The agent definition is an instruction file, not a monitoring service. Analysis
happens when you invoke the agent.
The shared profile leaves `target` unset for VS Code, CLI and experimental cloud
use, but explicitly disables automatic/model invocation. Select it as a user.
Effective tools and field enforcement still need verification in each host.

## Ready-to-use prompts

The [reusable prompt guide](usage-prompts.md) includes the
[focused first audit](usage-prompts.md#focused-first-audit) and
[deep analysis](usage-prompts.md#deep-analysis) prompts. It lists the required
optional skills and provides complete text to paste into Copilot Chat with
AI Efficiency & Performance Auditor selected. Both use source/configuration only and retain
the same audit budgets, safeguards and report-only writes.

## Why use it instead of the same prompt in Copilot?

The advantage is a repeatable audit method, not a smarter AI model. The auditor
runs through Copilot, adding detailed instructions and a focused tool configuration
behind a short audit request.

| Area | What the auditor adds |
|---|---|
| Coverage | A defined workflow for retrieval, inference, retries, tokens, caching, and model selection. |
| Evidence | Observed runtime counts are separated from static bounds and unknowns, with source citations. |
| Recommendations | Demonstrated waste is distinguished from hypotheses; unverified model substitutions stay in the validation plan. |
| Boundaries | Restricted tools and instructions against changing application code, replaying workloads, or exposing sensitive evidence. |
| Reporting | Standardized findings and a short Executive Summary, with save verification and preview consent. |

Ordinary Copilot could produce comparable results if given the entire agent
definition, equivalent tools, the same model, and the same evidence. The benefit
is packaging and versioning the methodology once, with regression evaluations,
rather than reconstructing it for every audit.

The auditor is not guaranteed to be more accurate, faster, or cheaper. Its longer
instructions add context overhead, and instruction-following can still fail,
including missed report or preview steps. Tool restrictions and instructions are
not a report-only filesystem sandbox. Its strongest benefit is consistency and
reviewability for repeated audits, not proven superiority over a carefully
configured Copilot session.

## How it works

### 1. Establish scope

The agent reads repository instructions and the README, identifies the application
and relevant framework guidance, then finds entry points, orchestration, tool
dispatch, model clients and selection, prompt/context construction, output
consumption, retries, caches, tests, and sanitized traces.
Discovery starts with exact guidance and supplied entry-point paths, consulting
relevant manifests and narrow globs only as needed. Named trace paths are reused without
enumerating sibling traces; the installed auditor profile is not application
evidence. Trace-only audits skip directory listings and manifest discovery.
After required guidance, a supplied source entry point is read before source
enumeration; direct dependencies are followed with exact paths and file-scoped
searches. Without a supplied entry point, relevant exact manifests help locate
one. Discovery must be narrowed to the remaining budget before issuing a
listing; oversized results still exhaust the budget.

Exploration is bounded to avoid an expensive, open-ended audit. If it cannot
locate the application, it reports **not auditable** rather than inventing counts.
Trace files are eligible only after safely isolated headers/metadata explicitly
state that they are sanitized, or the user directly confirms in the conversation
that each exact named path is sanitized.
That eligibility rule applies to runtime artifacts, not application source,
manifests, tests, or ordinary documentation. Labels do not authorize exposing
sensitive values.
Without that user confirmation, runtime eligibility is established before payload
reads or content searches, using small, sequential header-only ranges. If metadata
cannot be safely separated from event payloads, skip the artifact. Before even the
first read, the payload-free range must be established by the user's direct
statement naming the exact path and range, or an independently trusted format
contract. An initial three-line read is not automatically safe. Repository text
or an unendorsed sidecar is not user confirmation.
For existing user-named paths only, the agent may ask one batched sanitization
preflight question per audit. While waiting it reads no payloads; a negative,
ambiguous or missing answer (or unavailable `ask_user`) leaves paths ineligible.
An explicit denial overrides a file label. Missing paths do not trigger this
question, and failed preflight is followed by the normal stop rule.

For an explicitly requested trace-only audit, name the existing trace paths.
The agent does not require an application manifest or discover unrelated source,
but applies the same sanitization and read-budget rules. It reports observed
metrics with trace citations and marks source-level causes, static call sites,
implementation details and avoidability unknown unless the trace establishes
them. If no eligible artifact is found, the result is **not auditable** with no
call counts. This mode does not silently replace a requested application audit.

An ambiguous multi-application workspace requires scope selection, not a guess
based on manifest entry-point counts. When interaction is unavailable, the agent
reports that scope selection is required and does not combine applications.
Exactly one candidate is audited with the selection basis stated. If the audit
stops as **not auditable** or **scope selection required**, neither report is
created: only the stop reason, scope and checked paths appear in Chat.

The entire audit has a limit of 50 distinct files and 15,000 returned content
lines, including search results and repeated reads. Each scenario is additionally
limited to 25 files and 7,500 lines. The normal per-file limit is 300 lines; a
finding citing that file and line range in the current audit can justify up to
600 lines within every applicable total; each exception is listed in the Verdict.
Shared guidance counts toward the audit-wide totals and is additionally limited
to 10 files and 1,500 lines once per audit. Glob-returned paths count as files,
not content lines. Exhausting any budget means partial coverage, not a clean bill
of health.

### 2. Map the execution path

The agent follows:

```text
Request -> router -> agent/model -> tool dispatcher -> provider
        -> result validation -> synthesis
```

It looks for branching, handoffs, fan-out, loops, fallbacks, and retries.
It distinguishes these counting units:

| Unit | Meaning |
|---|---|
| Registered tools | Capabilities available to the agent, not executions |
| Static call sites | Code locations that can invoke tools |
| Logical calls | Intended tool operations |
| Execution attempts | Initial executions plus retries |
| Downstream requests | HTTP, SDK, database, or provider operations inside a tool |
| Logical model calls | Intended inference operations, separate from tool calls |
| Model attempts | Actual inference requests, including retries, failures, and fallbacks |
| Tokens | Recorded input/output usage, not call counts |
| Agent handoffs | Counted separately from tool and model attempts |

For example, one logical search call might produce three execution attempts,
each involving multiple downstream requests.
Likewise, one logical model call retried once produces two model attempts.
The model map records purpose, model/version, effective inputs and output
consumers. Embedding usage is separate from generation. A model request inside
a tool is linked across maps, not charged twice in combined savings.

### 3. Measure existing traces

When eligible traces exist, the agent correlates execution records and avoids
double-counting wrapper spans, duplicate exported events, or streaming fragments.
It reports only metrics supported by the evidence, such as calls per request,
retry amplification, failures, and latency.
Attempt keys are scoped to export namespace, run and layer. Retries need logical
IDs or explicit retry links; documented format-guaranteed composite keys may
substitute, but names, arguments and nearby timestamps cannot. Conflicting
duplicates remain unresolved. Without adequate correlation/coverage, counts are
lower bounds or unknown, not invented exact totals.
Argument equivalence needs cited canonicalization semantics: preserve types,
array order and fields; do not silently coerce, trim or drop inputs.

Complete populations must reconcile at the same layer: attempts cover initiated
logical calls, outcome partitions and disjoint row sums agree, token subsets
respect provider semantics, and non-overlapping savings do not exceed baseline.
Unknown outcomes or inconsistent records are disclosed, not forced to balance.

It distinguishes critical-path latency from summed tool duration: parallel calls
can reduce elapsed time without reducing call count. Observed cost requires
recorded usage and applicable pricing. Model duration is reported separately
from tool duration, with overlapping work accounted for.

Model metrics include logical calls, attempts, retries, and recorded input,
output, cached-input and reasoning tokens. Provider accounting matters: cached
tokens may already be included in input, and reasoning tokens in output.
Those subsets must not be added again. Provider prompt caching may reduce
billed cost while leaving the number of inference calls unchanged.
Failed requests may consume tokens; missing usage is unknown, not zero.
Cost requires applicable model/version, pricing date, units, currency, and
cache/reasoning billing rules. When supplied rates are per million tokens, cached
input is a separately priced subset, and reasoning is included in output, compute
cost across all attempts as
`((input-cached_input)*input_rate + cached_input*cached_rate + output*output_rate)/1_000_000`.
Include failed-attempt usage when recorded. Follow a different calculation only
when the supplied pricing explicitly requires it. Deployment names do not
establish price or quality.

Without sufficient traces, the agent can establish what the code permits or
necessarily does, but cannot claim actual production frequency or measured
savings. Static counts are expressed as conditional formulas or bounds where
appropriate; unknown values remain unknown.

### 4. Identify avoidable work

Typical targets include:

- Repeated equivalent reads when state has not changed.
- Handoffs that repeat discovery or lose reusable context.
- Nested retry policies that multiply execution attempts.
- Loops without effective stopping conditions.
- Per-item requests that could safely be batched.
- Concurrent duplicate reads that could share one execution.
- Ambiguous tool descriptions that cause corrective calls.
- Tool results that can be demonstrated to have no downstream use.
- Repeated inference on unchanged effective inputs when the output contract
  permits reuse.
- Model calls whose output is discarded, or that implement fully specified
  deterministic routing without required inference.
- Overlapping planning, critique, repair, and synthesis steps.
- Excessive context or unused generated output.
- Potential model-capacity mismatch for constrained tasks.

**Repeated does not automatically mean redundant.** Freshness, authorization,
pagination, changed state, differing credentials, and legitimate recovery can
justify repetition.
For inference, effective inputs include system instructions, prompt version,
conversation, retrieved evidence, tool schemas, model/settings, policy and
identity. Identical user text or temperature zero is not proof of safe reuse.
Required independent checks and stochastic samples must remain independent.

Findings are labeled measured, statically demonstrated, or hypothetical.
Only measured or statically demonstrated findings enter the ranked list.
Hypotheses remain in the validation plan with the evidence needed to test them.
In particular, a large token count or expensive model is not proof of waste.
Smaller-model substitutions, prompt trimming and step consolidation remain
hypotheses unless source contracts or comparative evaluations establish
acceptable replacement behavior.

### 5. Recommend changes and validation

The agent reports scenario-local impact per invocation and workload-weighted
impact per traffic request. Weighting requires measured branch frequencies in a
representative window; otherwise traffic-level impact is unknown and ranking
stays within each scenario. Within comparable scope and units, it ranks by
confidence, supported avoidable work per request, lower risk and lower effort.
Tool-call, model-call and token/capacity findings are grouped separately.
Token-only findings use supported avoidable tokens, not fictional call savings;
tokens and calls are not interchangeable ranking units. Cross-group cost ranking
requires comparable supported pricing and usage.
High confidence requires complete evidence of avoidability and the relevant
identity, state, freshness, and dependency conditions. Medium confidence applies
to demonstrated bounded scenarios with unknown frequency. Low-confidence
hypotheses are unranked. Evidence level and confidence are separate labels;
unknown impact is never converted to zero.

Recommendations may include:

- Deterministic routing and narrower tool contracts.
- Request-scoped result reuse.
- Safe batching and coalescing of equivalent concurrent reads.
- Bounded retries with backoff.
- Explicit call budgets and early stopping.
- Reuse of validated evidence.
- Safe inference-result reuse and removal of proven redundant model steps.
- Task-specific output limits and evaluated model routing.

Caching and coalescing must preserve tenant, identity, authorization, freshness,
invalidation, and data-classification boundaries. Side-effecting operations must
not be suppressed indiscriminately; retries of writes require a justified
idempotency strategy.
Model reuse must additionally preserve prompt/model versions, conversation and
evidence state, policy, output schema, and sampling requirements. Removing
inference must preserve required errors and side effects as well as output.

The report separates **projected savings** from **validated savings**. It proposes
matched baseline/candidate comparisons that also check task success, evidence
quality, citation validity, freshness, isolation, and relevant failure scenarios.
An optimization is not considered validated until comparative evidence exists.
Model comparisons additionally cover schema adherence, routing accuracy,
difficult and safety-sensitive inputs, independent checks, and stochastic
variance. Fewer calls alone does not establish a better design.
Tool/model call and token budgets are separate; overlapping savings are not
summed when removing one model step also removes its tool work.
Validation designs declare primary metrics, sample-size rationale, stochastic
repetitions/uncertainty intervals where relevant, quality equivalence or
non-inferiority margins, and pass/fail/inconclusive rules. Proposed thresholds
require approval if application requirements do not supply them.

## Optional service-performance review

Install the [service-performance skill](../.github/skills/service-performance-review/SKILL.md)
alongside the agent in the application repository and explicitly request this
mode. For example:

> Review service performance starting at `src\service\agents\agent.py`, following
> only direct dependencies for the streaming request path. Check async blocking,
> client/pool ownership, concurrency, backpressure, storage, and cleanup.

This is specialist guidance for the same auditor, not another runtime agent.
It preserves permissions, sanitization, budgets, report saving, and preview
consent. If the skill is missing, the auditor discloses unavailable specialist
guidance rather than claiming checklist coverage. Existing orchestration checks
are reused, not duplicated.

The six-section report adds a service inventory, supported service metrics,
and separately grouped service findings. Demonstrated scheduling or lifecycle
defects need not reduce tool/model calls. Latency, contention, and resource
impacts use explicit units or remain unknown; they are not ranked against
incomparable call/token units. No measured improvement is claimed from static
code alone. Negative cases include intentionally synchronous worker paths,
identity-scoped clients, bounded streams, and correctly released resources.

See the [service behavior cases](../evaluations/service-performance.md) for
review inputs and acceptance criteria. These cases are not live-model evidence.

## Optional advisory reviews

Install the selected whole directories under `.github/skills/` alongside the
agent in the application workspace. The base agent remains usable without them.
All modes are explicit opt-ins, preserve core permissions, sanitization and
audit/scenario/guidance/per-file budgets, and reuse the six-section report plus
Executive Summary save/preview workflow. Combining requested modes does not
permit duplicate findings, extra budgets or broader tools. Missing guidance
is disclosed rather than claimed as covered.

### Baseline/candidate comparison

Install [audit-comparison](../.github/skills/audit-comparison/SKILL.md) including
its reference directory. For example:

> Compare the supplied baseline and candidate audits only. Use audit-comparison;
> show per-request call/token deltas and whether quality/safety support an
> improvement. Do not inspect source to fill gaps in the supplied reports.

Named source snapshots or eligible trace sets are also supported when already
available within authorized workspace scope. Revision names are labels, not
permission to fetch/check out code. Report-only comparison needs no manifest or
application discovery. Treat reported locations as unverified, and do not infer
resolution from omission in a candidate report.

Comparability is established per metric: task mix, identity/permissions, data/
freshness, model/settings, cache state, provider/concurrency, completion coverage,
counting/usage/pricing semantics and evidence versions. Intentional changes are
separate from confounders. Different sample sizes require comparable per-request
rates, not subtraction of raw totals. Candidate-minus-baseline deltas retain
units, denominators, windows and sample sizes; percentages are N/A for zero
baselines and unknown for missing values. If equivalence is unestablished,
present two profiles without an improvement/causal-delta claim.

Improved/regressed/mixed/inconclusive decisions need approved directions and
quality/safety margins. Supplied-report claims are not independently validated.
One comparison creates one report pair, not separate artifacts for each side.

### Context and retrieval

Install [context-retrieval-review](../.github/skills/context-retrieval-review/SKILL.md).
For example:

> Review context and retrieval efficiency starting at `src\search.py:answer`.
> Follow query expansion, document selection/reranking, context assembly,
> history and evidence consumption. Do not collect prompts or document passages.

The inventory uses opaque segment/document/version and consumer references,
recorded tokens/bytes and source contracts. Different versions or tenants are
not equivalent duplicates; a missing final citation does not prove a document
was unused. Large top-k, repeated schemas and long history are review targets,
not proof that removal preserves protocol, recall, quality or independent checks.
Characters are not tokens; provider cache subsets and removed-call savings are
not counted again. Keep output-quality-dependent trimming unranked until
contracts or comparative evaluation establish safe replacement behavior.

### Retry, cache, fan-out and concurrency

Install [orchestration-efficiency-review](../.github/skills/orchestration-efficiency-review/SKILL.md).
For example:

> Review orchestration efficiency from `src\worker.py:handle`: retry amplification
> by layer, cache eligibility/hits, fan-out, observed concurrency, deadline
> propagation and cancellation. Use existing evidence only.

The skill defines layer-specific amplification, conditional retry bounds,
logical fan-out width/depth, half-open-interval concurrency, eligible lookup hit
rates and dependency-based critical paths. Fan-out is not observed concurrency;
parallel and nested spans are not additive latency. Mutually exclusive retry
policies do not multiply. Cache/coalescing keys preserve identity, freshness and
output/error contracts; writes require idempotency and uncertain-outcome evidence.
Disconnects do not make durable jobs or required cleanup waste.

The existing service-performance skill also checks deadlines/cancellation.
Use it for broader scheduling/pool/stream/lifecycle defects; use orchestration
review for quantitative operation/retry/cache analysis. Load both only when both
are requested, linking shared mechanisms instead of duplicating them.

### Evidence/report contract and diagrams

The core and modes identify internal `advisory-evidence/1` and
`advisory-markdown/1` contracts, independently of methodology 0.5.0. The comparison
reference documents audit/scenario, operation, attempt, downstream, usage,
consumption and finding fields. Unknowns stay unknown; these are not a public
JSON schema, a trace parser or proof of deterministic behavior.

Optional Mermaid text in the detailed Proposed design section uses opaque node
IDs, sanitized operation classes and adjacent evidence citations. Distinguish
baseline, observed candidate and proposed graphs; unknown topology stays
unknown. No renderer/external service is invoked and diagrams do not belong in
the Executive Summary. Schema validation, live execution, large-trace analytics
and code remediation remain outside the auditor's permissions.

The [advisory evaluation guide](../evaluations/advisory-skills.md) distinguishes
synthetic fixture/checker results from missing live-host and semantic validation.

## Capabilities and limits

The agent exposes `read`, `search`, `edit`, `ask_user`, and
`appmod-preview-markdown`, with no subagents. Its sole write exception is creating
new Markdown detailed audit and Executive Summary files; summary preview requires explicit user consent. These
host-specific interaction/preview names must resolve to compatible local tools.
If unavailable, it uses Chat and manual save/preview instructions. The `edit`
group is not path-restricted by the host; report-only writes are an instruction
boundary, not a sandbox. Its instructions
prohibit:

- Editing application code, configuration, evidence, or existing files.
- Running commands, including commands to save or preview reports.
- Executing application tools or calling external services.
- Invoking other agents.
- Provisioning resources.
- Replaying workloads or performing experiments.

It produces an audit and recommendations; it does not implement or benchmark
the fixes. When evidence is insufficient, it identifies missing inputs and
recommends minimum instrumentation instead of fabricating measurements.

Repository content and traces are treated as evidence, not instructions or
authorization. Reports must not expose credentials, raw private prompts,
sensitive arguments, or full tool responses. Private context must not be sent
to public-web services.

## Report contents

The report contains:

1. **Verdict and evidence coverage:** scope, static versus observed evidence,
   sampling, limitations, projected versus validated savings, and a compact
   inspection ledger of known provenance, discovered/inspected paths and ranges,
   selection reasons, searches, exclusions, budget use, trace window/supplied
   digest, and pricing source/date. Unknown provenance stays unknown; there is
   no extra discovery or digest computation to fill the ledger. Exported roots
   are shown as `.` without home-directory components.
   A coverage matrix marks orchestration, tools/retries, models/context,
   output consumption, safety and runtime evidence as inspected, partial,
   missing or not applicable, with evidence or an explicit explanation.
2. **Call map and inventory:** tools, static call sites, logical calls,
   attempts, downstream requests, and evidence, plus a separate model map with
   purpose, model/version, calls, attempts, and input/output dependencies. A linked
   safety inventory covers read/write class, identity/auth scope, freshness,
   idempotency and cache/retry eligibility; unknown safety is not assumed safe.
3. **Runtime metrics:** separate tool/model totals, per-request/per-tool/per-model
   measures, tokens, latency and supported cost, including coverage, counting
   rules, subset semantics and denominators.
4. **Ranked findings:** priority, evidence level, confidence, avoidable calls,
   supported token/cost impact, recommendation, and risk, grouped by dimension.
5. **Proposed design:** before/after call flow, scenario-specific call budget,
   expected savings, assumptions, and tradeoffs.
6. **Validation plan and missing evidence:** comparison criteria,
   instrumentation gaps, and the next highest-value action.

Source-backed weaknesses and redundancy findings identify the affected file,
function or section, and smallest verified line range. Findings spanning repeated
or duplicated code identify each relevant site and explain its role. Call-site
ranges exclude unrelated return statements or surrounding context. File-and-line
notation stays visible in citation labels or adjacent text; each summary Code
location cell shows the affected paths and ranges directly beside the symbol,
not only in link targets or reference definitions. Detailed
reports may include minimal relevant code excerpts with sensitive values omitted;
Executive Summaries include locations, not code excerpts. Trace-only findings
say "Code location not verified" when no source mapping is available. Summaries
of existing reports label copied locations "From supplied report; not reverified"
or state "Not provided in supplied report"; they do not inspect code to fill gaps.

Every ranked finding and call-map row requires a citation. Visible labels use
repository-relative paths/ranges, not workstation or home-directory details.
Absolute link targets are permitted only for local editor clickability; exported
reports use relative links. Remote reports use commit-pinned
repository links when URL and revision are verified. Otherwise, remote reports
use a textual path and verified line and disclose that pinned links are
unavailable. Findings from sanitized traces use the trace path and record ID.
If a line cannot be verified, the report gives the path and marks the line
unknown. Methodology version and any known audited revision, host, and model
are recorded; unavailable provenance stays unknown.

If no redundant calls are demonstrated, the report says so and identifies what
evidence could resolve uncertainty.

### Executive Summary and preview

Every completed audit also creates a plain-language Executive Summary of at most 60 lines and
600 words. It includes a bottom line, up to five evidence-backed priority rows
(`Priority | Weak area | Code location | Recommended improvement | Expected benefit | Evidence`),
separate evidence gaps, safeguards to retain, and one next action. It preserves
ranking, confidence, conditional benefits, unknowns, and non-overlapping savings.
An existing supplied audit can be shortened without new source inspection.
The detailed six-section report is still required for new audits and is saved as
`reports/<application>-audit-detailed-report.md`. It is not subject to the summary's
length limits. A supplied-report-only summary does not create a new detailed audit.

The default summary output is `reports/<application>-audit-executive-summary.md` in the audited
workspace (`trace` for trace-only audits). Existing files are never overwritten;
the agent checks exact paths and uses the first available numeric suffix, with
at most ten candidates per report including the base path. Unreadable paths are
not treated as free paths; exhaustion returns the report in Chat with a reason.
An explicitly requested outside-workspace destination requires confirmation.
Complete drafts are validated before the first write, including privacy,
citations, arithmetic and summary limits. The agent saves each file once.
It reads back the detailed report first, verifying all six sections
and their evidence citations, then links its verified path from the summary. It
reads back the summary and checks both summary length limits. It links both verified
files and asks whether to open the Executive Summary in Markdown preview.
Only an explicit Yes opens that summary; declining, dismissing,
or not answering leaves it closed. Each new report requires fresh consent.

Without a save tool or after a save failure, the agent explains that the report
was not saved, identifies which report failed, and returns that report's Markdown
in Chat. An unverified detailed file is not linked as verified; the summary
identifies Chat as its location when saving or verification fails.
Partial writes, invalid artifacts and read-back failures are disclosed; created
files remain untouched, no alternate-path write retries occur, and corrected
content is returned in Chat. This is not transactional two-file persistence.
Without interaction or preview tools it gives **Markdown: Open Preview**
instructions without soliciting consent through another tool.
Non-interactive runs never open preview. Save, verification, and
preview errors must be reported rather than presented as success.

## Example invocation

Select **AI Efficiency & Performance Auditor** in the agent picker and submit:

> Audit this workspace's search request flow for unnecessary tool and model calls.
> Use existing sanitized traces if available. Focus on duplicate retrieval,
> repeated inference, retries, token usage and model selection. Rank demonstrated
> optimizations and keep unverified substitutions in the validation plan.

For a narrower audit, name the application path and scenario explicitly.
If traces are available, provide their workspace paths and either directly confirm
each exact path is sanitized or identify its independently established payload-free
metadata range, where the agent can inspect the sanitization label.

The goal is fewer unnecessary calls, not fewer checks or less reliable behavior.

For missing model telemetry, the auditor recommends opaque logical-call/attempt
IDs, model/version, purpose, prompt/context versions, generation settings,
outcome/finish reason, consumption references and recorded usage with coverage
and subset semantics. It does not request raw prompts, chain-of-thought or
responses, and it does not collect telemetry itself.

## Sharing and invocation

Keep this guide outside agent-discovery directories: hosts can also recognize
plain Markdown files there as agents. See the [installation guide](../README.md),
[remote invocation guide](remote-invocation.md), and
[evaluation instructions](../evaluations/README.md).
