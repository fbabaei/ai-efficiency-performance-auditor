# Choose-your-goal prompt catalog

Open the application repository you want to audit in VS Code and select
**AI Efficiency & Performance Auditor** in Copilot Chat. Install the agent in
`.github\agents\` and the required whole skill directories in `.github\skills\`
inside that application repository, including any bundled references.
See the [installation guide](../README.md#install-in-the-repository-you-want-to-audit).

New users: follow the [quick start](quick-start.md), then pick **one goal** below.
You do not need to install every skill or run every prompt. All Chat prompts use
the same auditor agent; skills are optional checklists, not separate agents.

## Choose your goal

| Stage | I want to... | Start here | Required skill or tool |
|---|---|---|---|
| Beginner | Review one AI request flow | [Base source-only audit](#base-source-only-audit) | Base agent only |
| Beginner | Understand an existing report | [Summarize an existing report](#summarize-an-existing-report) | Base agent only |
| Focused review | Find repeated retrieval or growing context | [Context and retrieval](#context-and-retrieval) | `context-retrieval-review` |
| Focused review | Review retries, caching or parallel work | [Orchestration efficiency](#orchestration-efficiency) | `orchestration-efficiency-review` |
| Focused review | Review streaming, pools or cleanup | [Service performance](#service-performance) | `service-performance-review` |
| Combined review | Review tool/model efficiency together | [Focused first audit](#focused-first-audit) | Context + orchestration skills |
| Combined review | Include service lifecycle checks too | [Deep analysis](#deep-analysis) | Context + orchestration + service skills |
| Next steps | Turn findings into developer tasks | [Recommendation planning](#recommendation-planning) | `recommendation-planning` |
| Next steps | Decide what to measure | [Measurement readiness](#measurement-readiness) | `measurement-readiness` |
| Change review | Review proposed code changes | [Change-impact review](#change-impact-review) | `change-impact-review` |
| Before/after | Compare two existing reports | [Baseline/candidate comparison](#baselinecandidate-comparison) | `audit-comparison` with references |
| Before/after | Verify individual fixes | [Finding-level verification](#finding-level-verification) | `audit-comparison` with references |
| Runtime evidence | Review sanitized traces without source | [Trace-only audit](#trace-only-audit) | Base agent; eligible trace inputs |
| Offline tooling | Import an existing sanitized OTLP export | [Import command](offline-tooling.md#import-already-sanitized-otlp-json) | Run Python companion yourself |
| Offline tooling | Calculate approved budget checks | [Gate command](offline-tooling.md#evaluate-approved-budgets) | Run Python companion yourself |
| Results | Understand an existing gate result | [Efficiency-budget interpretation](#efficiency-budget-interpretation) | `efficiency-budget-review` |

## Optional editable insertion

Instead of copying a template, install the separate
[Auditor Prompt Picker extension](prompt-picker.md). Open **Auditor: Insert Prompt**
from the Command Palette and type a picker name such as `/audit-start` or
`/audit-context`. Select it and confirm replacement of any existing Chat draft.
The full template is inserted as editable, unsent text; edit its inputs and send
it yourself. The guide lists all 14 names and installation/host-check steps.

Picker names are not native Copilot slash commands. Agent selection, required
skills, input safety and attachments remain your responsibility. The extension
does not expand typing directly in Copilot's input or execute a prompt.

## Before you paste

- Replace every `<placeholder>` with a real, exact workspace path or value.
  An **entry point** is the source file/function where your chosen request starts.
  A **scenario** is one task, such as answering a search question.
- Start with one flow. The source-review templates need no runtime traces;
  they follow only relevant dependencies within the existing audit budgets.
- Install only the named skills, copying whole directories and bundled
  references. Missing guidance should be disclosed, not fetched or installed.
- The auditor recommends changes; it does not edit your application, execute
  commands, fetch PRs/revisions, collect telemetry or run offline tools.
- New audits use the six-section detailed report and bounded Executive Summary,
  core no-overwrite/read-back rules and explicit consent before summary preview.
  The summary-only template deliberately creates no new detailed audit.
- Sanitize runtime files before use. A copied template is **not** sanitization
  confirmation. Endorse only exact paths you have actually checked; otherwise
  keep them unread until the core eligibility gate is satisfied. Do not paste
  secrets or raw private prompts/responses.
- Source-based opportunities are not measured savings. Unknown or inconclusive
  results are useful evidence gaps, not zeros, failures of the tool or passes.

## Base source-only audit

**When:** Your first review of one AI application flow.<br/>
**Install:** Base agent only; no optional skill.<br/>
**Inputs:** One actual entry-point path and a short scenario description.<br/>
**Expect:** Supported findings, code locations, priorities and validation gaps.<br/>
**Next:** Read the summary, then use [recommendation planning](#recommendation-planning)
for supported changes or [measurement readiness](#measurement-readiness) for gaps.

```text
Audit this scenario: <one task the application performs>.
Start at <actual entry-point path and function if known>.

Use source code and configuration only. Follow necessary direct dependencies
within the existing audit budgets. Do not read traces, run commands/workloads,
load optional review modes or modify application files.

Look for unnecessary tool/model calls, repeated retrieval, retry amplification
and unused results. Explain only demonstrated issues as ranked findings, cite
exact code locations and preserve authorization, freshness, quality and recovery.
Keep hypotheses and unknown runtime benefits in the validation plan.

Recommend the smallest safe changes and checks without performing them.
Save one detailed report and one Executive Summary under reports\ without
overwriting existing files. Read both back and ask before summary preview.
```

## Summarize an existing report

**When:** You want a shorter explanation, not another application audit.<br/>
**Install:** Base agent only.<br/>
**Inputs:** One exact existing audit report path or the report pasted in Chat.<br/>
**Expect:** A new concise Executive Summary; no new detailed report or source review.<br/>
**Next:** Share the summary, or use [recommendation planning](#recommendation-planning)
to prepare developer handoff cards.

```text
Shorten this supplied report into a plain-language Executive Summary only:
<exact existing audit report path, or report pasted below>

Do not conduct a new audit, inspect the codebase or open referenced traces.
Preserve the report's priorities, confidence, safeguards and unknowns.
Label copied locations "From supplied report; not reverified"; absent locations
are "Not provided in supplied report". Do not invent sites or numerical savings.

Use the existing six-column summary table and limits of 60 lines and 600 words.
Do not copy source code. Save one new summary Markdown file under reports\
using the core no-overwrite workflow, and read it back before linking it.
Do not generate or copy a new detailed audit. Ask before previewing the summary.
```

## Context and retrieval

**When:** Retrieval repeats, conversation history grows, or too much context
seems to be sent to a model.<br/>
**Install:** `context-retrieval-review` only.<br/>
**Inputs:** One retrieval/answer entry point and scenario.<br/>
**Expect:** Context/retrieval inventory, supported waste and quality-dependent hypotheses.<br/>
**Next:** Use [measurement readiness](#measurement-readiness) for missing
consumption/token evidence, or [recommendation planning](#recommendation-planning).

```text
Explicitly use context-retrieval-review for this scenario: <task>.
Start at <actual retrieval or answer entry-point path>.

Use source and configuration only; no runtime traces or private prompt/passages.
Follow query transformation, selection/filtering, reranking, embedding reuse,
context assembly, history, repeated schemas and downstream result consumption.
Load no other optional mode. Stay within the core exploration budgets.

Check exact document/content versions, tenant/authorization scope, freshness,
input contracts and independent consumers before calling repeated work avoidable.
Missing final citations do not establish unused retrieval; characters are not
tokens. Lower top-k, trimming history or removing a reranker needs quality evidence.

Cite all relevant source sites. Separate demonstrated removable work from
unranked hypotheses; do not invent token counts or measured savings.
Propose the smallest safe changes and recall/quality/freshness checks.
Do not edit code, collect content, run commands/workloads or call services.
Save one six-section report and Executive Summary under reports\ without
overwrites; verify both and ask before summary preview.
```

## Orchestration efficiency

**When:** You suspect excess retries, repeated work, fan-out or ineffective caching.<br/>
**Install:** `orchestration-efficiency-review` only.<br/>
**Inputs:** One handler/orchestrator path and scenario, including a failure path if known.<br/>
**Expect:** Layer-specific operation/retry analysis and evidence-qualified opportunities.<br/>
**Next:** Use [recommendation planning](#recommendation-planning) for supported
changes or [trace-only audit](#trace-only-audit) after preparing eligible evidence.

```text
Explicitly use orchestration-efficiency-review for <scenario>.
Start at <actual handler or orchestration entry-point path>.

Use source/configuration only and load no other optional mode.
Follow orchestration, tool and transport retries, fallbacks, fan-out, cache/reuse
eligibility, deadlines, cancellation and result consumers within core budgets.

Separate logical operations, attempts and downstream requests at each layer.
Multiply retry limits only on a demonstrated nested branch; exclusive branches
do not multiply. Static fan-out is not observed concurrency or measured latency.
Repeated work is not automatically avoidable.

Preserve identity, freshness, idempotency, uncertain write outcomes, recovery,
required cleanup, durable accepted jobs and independent consumers.
Rank only demonstrated mechanisms; unknowns and conditional bounds stay explicit.
Propose changes and matched failure/quality checks without executing them.
Do not edit code, run commands/workloads, inspect traces or call services.
Save one six-section report and Executive Summary under reports\ without
overwrites; verify both and ask before summary preview.
```

## Service performance

**When:** A service may block, recreate clients, mishandle streams or leak owned resources.<br/>
**Install:** `service-performance-review` only.<br/>
**Inputs:** One actual request/stream handler and scenario.<br/>
**Expect:** Source-backed service defects, ownership/cleanup evidence and validation needs.<br/>
**Next:** Use [measurement readiness](#measurement-readiness) to plan runtime
measurements, or [recommendation planning](#recommendation-planning) for handoff.

```text
Explicitly use service-performance-review for <request or streaming scenario>.
Start at <actual service handler path>.

Use source/configuration only and no other optional mode. Follow admission,
handler, clients/storage, response/stream, cancellation and cleanup paths.
Review reachable async blocking, client/pool ownership and reuse, concurrency,
streaming backpressure, storage access, deadlines and resource lifecycle.

Establish execution context, ownership and effective bounds before declaring a
defect. Synchronous names or missing local caps alone are not proof of waste.
Preserve identity isolation, transactions, error reporting, necessary cleanup,
durable work and independent consumers.

Rank demonstrated service defects even when no call reduction is established.
Keep latency, contention and leak magnitude unknown without measurements.
Propose overload, slow-consumer, disconnect, failure and shutdown checks.
Do not edit code, install instrumentation, inspect traces or run commands,
benchmarks or workloads. Do not call services.
Save one six-section report and Executive Summary under reports\ without
overwrites; verify both and ask before summary preview.
```

## Recommendation planning

**When:** An audit has supported findings that need developer handoff.<br/>
**Install:** `recommendation-planning`.<br/>
**Inputs:** One exact existing report path or a report pasted in Chat.<br/>
**Expect:** Proposed cards with dependencies, safeguards, effort, acceptance and rollback.<br/>
**Next:** Implement separately, then use [finding-level verification](#finding-level-verification)
when matched candidate evidence and approved quality/safety results are available.

```text
Use recommendation-planning on this supplied report only:
reports\<application>-audit-detailed-report.md

Do not discover an application, inspect source or read traces to fill gaps.
Treat reported findings and locations as supplied claims, not reverified evidence.
Preserve finding IDs; label any new IDs as audit-local.

For each supported mechanism, propose the smallest change with evidence and
locations, dependencies/blockers, safeguards, expected-effect assumptions,
effort with rationale or unknown, proposed acceptance checks and rollback triggers.
Keep missing safety contracts blocked and unproven changes unranked in the
validation plan. Do not invent savings or claim implementation or resolution.

Keep the existing six sections. Put supported cards in Proposed design and
summarize the highest-priority actions in the Executive Summary.
Save one new report pair under reports/ without overwriting existing files.
Ask before opening the summary preview. Do not edit code, create task files or
tickets, run commands/tests, call external services or invoke other agents.
```

For cards alongside a new audit, append "Explicitly use recommendation-planning
for supported findings" to either source-audit prompt below; install all skills
that prompt requests. This does not add a separate audit or exploration budget.

## Change-impact review

**When:** You want to review proposed changes rather than the whole application.<br/>
**Install:** `change-impact-review`.<br/>
**Inputs:** An exact existing diff path, pasted diff, or named baseline/candidate
source snapshots. A PR URL or branch name alone is not evidence.<br/>
**Expect:** Introduced/pre-existing/unknown attribution with side-aware citations.<br/>
**Next:** Use [recommendation planning](#recommendation-planning) for supported
corrections or [baseline/candidate comparison](#baselinecandidate-comparison) later.

```text
Explicitly use change-impact-review on this supplied diff only:
reviews\<change>.diff

Review the changed AI request path for introduced repeated retrieval/inference,
retry amplification, context growth, unused results and affected dependencies.
Do not fetch a PR, run Git, apply the diff, inspect other source or read traces.
Treat incomplete hunks and missing contracts as coverage gaps.

Cite old/new sides and hunks without presenting them as reverified source.
Distinguish introduced regressions, pre-existing mechanisms, candidate defects
with introduction unknown, and unranked hypotheses. Preserve authorization,
freshness, idempotency, output quality, safety checks and necessary recovery.
Do not infer runtime savings or whole-PR safety from a static diff.

Keep the six report sections and the existing Executive Summary limits.
Propose the smallest correction and regression/quality checks; do not run them.
Save one new report pair under reports/ without overwriting existing files.
Ask before opening the summary preview. Do not edit code, create tickets,
post PR comments, call external services or invoke other agents.
```

For source-backed follow-up, explicitly authorize exact local candidate and
baseline paths plus the necessary direct dependencies. For developer handoff,
also explicitly request `recommendation-planning` and install that skill;
both modes share the evidence budget, finding IDs and report pair.

## Measurement readiness

**When:** You cannot yet measure or verify an audit recommendation.<br/>
**Install:** `measurement-readiness`.<br/>
**Inputs:** One exact audit report; for a source-backed request, name the entry point
and explicitly authorize that scope instead.<br/>
**Expect:** Ready/partial/blocked decisions, missing metadata and privacy-conscious proposals.<br/>
**Next:** Collect approved measurements separately; use the
[offline gate](offline-tooling.md#evaluate-approved-budgets) or comparison afterward.

```text
Explicitly use measurement-readiness on this supplied report only:
reports\<application>-audit-detailed-report.md

Do not inspect source or traces to fill gaps. For each finding, identify the
decision, existing evidence, missing metadata, source site or unknown, population
and units, privacy/retention safeguards, overhead and required approvals.
Propose payload-free measurements and positive/negative/error-path checks.
Mark readiness per decision; absence of telemetry is not proof of waste.
Do not install instrumentation, collect telemetry, run workloads or invent
quality thresholds. Retain the six sections and one report pair.
```

## Baseline/candidate comparison

**When:** You want to understand differences between a before and after audit.<br/>
**Install:** `audit-comparison`, including the whole `references\` directory.<br/>
**Inputs:** Two exact existing report paths labeled baseline and candidate.<br/>
**Expect:** Comparability assessment, supported deltas and qualified conclusions;
supplied claims are not independently validated.<br/>
**Next:** Use [finding-level verification](#finding-level-verification) for
individual fixes, or [measurement readiness](#measurement-readiness) for gaps.

```text
Explicitly use audit-comparison to compare these supplied reports only.
Baseline: <exact existing before-report path>
Candidate: <exact existing after-report path>
Scenario: <the task being compared>

Do not discover an application, inspect source/traces, run evaluations or fetch
revisions. Keep report locations and claims attributed, not independently reverified.
Check workload, completion coverage, quality/safety contract, identity/freshness,
cache/deployment conditions, units and denominators before comparing metrics.

Show candidate-minus-baseline deltas only for comparable known values.
Use per-request rates where justified, not unlike raw totals. Zero baseline
means N/A percentage; missing values stay unknown. If comparability is missing,
show separate profiles without an improvement or causal-delta claim.

Keep calls, attempts, tokens, elapsed latency and cost separate and avoid
overlapping savings. Fewer calls alone do not prove quality-preserving improvement.
Missing candidate findings do not prove resolution.
Save one six-section comparison report and Executive Summary under reports\
without overwrites; verify both and ask before summary preview.
```

For source snapshots, replace both report paths with exact existing snapshot
paths and explicitly permit reads of those snapshots only. Do not substitute
the current checkout for unavailable revisions. For runtime comparisons, name
each eligible trace set and apply the exact-path sanitization gate separately;
the report-only template above intentionally does not open traces.

## Finding-level verification

**When:** You need the status of specific fixes, not just metric differences.<br/>
**Install:** `audit-comparison` including its bundled references.<br/>
**Inputs:** Actual both-side evidence and approved quality/safety criteria/results
or an explicit statement that they are missing.<br/>
**Expect:** Evidence-qualified per-finding status; no resolution from plans or omissions.<br/>
**Next:** Address partial/persistent/regressed items; collect the named evidence
for inconclusive ones. The prompt does not authorize fetching revisions.

```text
Explicitly use audit-comparison for finding-level optimization verification.
Baseline: <exact existing baseline report or snapshot path>
Candidate: <exact existing candidate report or snapshot path>
Quality and safety criteria/results: <exact supplied evidence or state missing>

Match finding IDs with scenario, mechanism, operations and affected-site coverage.
Report verified-fixed, partially-addressed, persistent, regressed or inconclusive,
with both-side citations and remaining gaps. Do not infer resolution from
omitted findings, a plan, deleted code or fewer calls. Keep static mechanism
correction separate from measured benefit and preserved quality.
Use supplied inputs only. Do not run evaluations, fetch revisions or inspect
other source/traces. Create one report pair under the existing save/consent rules.
```

## Efficiency-budget interpretation

**When:** You already have a calculated offline gate result.<br/>
**Install:** `efficiency-budget-review`.<br/>
**Inputs:** Exact approved policy and result paths from the
[offline companion](offline-tooling.md), which you run yourself.<br/>
**Expect:** A plain-language explanation of each pass/fail/inconclusive check and its limits.<br/>
**Next:** Fix supported causes or use [measurement readiness](#measurement-readiness)
for missing evidence. Confirm exact-path sanitization before runtime artifact
reads; this template itself is not confirmation.

```text
Explicitly use efficiency-budget-review on these existing inputs:
Policy: <exact approved budget policy path>
Result: <exact gate result path>

Interpret supplied results only; do not run the companion or discover an app.
Show metric units, approved directions/thresholds, candidate/baseline values,
pass/fail/inconclusive checks and missing inputs or comparability evidence.
Passing budgets does not establish quality equivalence or finding resolution.
Keep unproven causes unranked and propose the smallest next validation step.
Retain the six sections, summary limits and existing report save/consent workflow.
```

## Focused first audit

**When:** You want a combined tool/model review of one representative request.<br/>
**Install:** `orchestration-efficiency-review` and `context-retrieval-review`.<br/>
**Inputs:** One scenario; add an actual entry-point path to narrow discovery.<br/>
**Expect:** One combined efficiency audit, not separate reports or extra budgets per mode.<br/>
**Next:** Use [recommendation planning](#recommendation-planning) or
[measurement readiness](#measurement-readiness).

```text
Audit this application's main AI request flow for avoidable tool/model calls,
retry amplification, duplicate retrieval, context growth and unused results.

Use orchestration-efficiency-review and context-retrieval-review explicitly.
Identify the application entry point and follow one representative request
end to end. If multiple applications are equally plausible, ask me to choose.

Use source code and configuration only for this first audit. Do not read
runtime traces, execute commands, run workloads or modify application files.

Rank only measured or statically demonstrated avoidable work. Cite exact
source locations, distinguish logical calls from attempts, and preserve
authorization, freshness, quality, idempotency and required safety checks.
Keep unproven savings and quality-dependent changes in the validation plan.

Save one detailed report and one Executive Summary under reports/, preserving
existing files. Ask before opening the summary preview.
```

## Deep analysis

**When:** You also need failure-recovery and service lifecycle checks.<br/>
**Install:** `orchestration-efficiency-review`, `context-retrieval-review` and
`service-performance-review`.<br/>
**Inputs:** One scenario; preferably a known request entry point.<br/>
**Expect:** A combined audit within unchanged permissions and exploration budgets,
not exhaustive application coverage.<br/>
**Next:** Plan supported fixes or measurements, then compare matched evidence.

```text
Perform a deep, evidence-backed efficiency review of this application.
Explicitly use orchestration-efficiency-review, context-retrieval-review
and service-performance-review.

Identify the main AI entry point and deeply follow one representative request,
including its failure/retry path. If multiple applications are plausible,
ask me to choose. Stay within the existing exploration budgets and disclose
uninspected branches rather than claiming exhaustive coverage.

Examine:
- Tool/model calls, nested retries, fallbacks and redundant operations.
- Retrieval, reranking, embedding reuse, context assembly, history growth
  and whether results are actually consumed.
- Cache eligibility, tenant/auth isolation, freshness and invalidation.
- Fan-out, concurrency controls, deadlines, cancellation and durable work.
- Async blocking, client/connection pooling, streaming, storage and cleanup.

Use source code and configuration only. Do not read runtime traces, execute
commands, run workloads, call external services or modify application files.

For each demonstrated finding, cite exact files, symbols and line ranges;
explain the mechanism, applicability, safeguards and simplest correction.
Separate logical calls, attempts, downstream requests and token effects.
Avoid overlapping savings. Do not infer measured latency, cost or concurrency
from static code, or assume repeated work is unnecessary.

Keep hypotheses unranked in the validation plan. Specify the smallest
experiment needed to confirm each important uncertainty, including quality,
correctness, security and failure-recovery checks. Do not run experiments.

Save one detailed six-section report and one Executive Summary under reports/,
without overwriting existing files. Ask before opening the summary preview.
```

The focused and deep-analysis prompts do not enable `audit-comparison`. Use
[baseline/candidate comparison](#baselinecandidate-comparison) separately.

## Trace-only audit

**When:** You have existing sanitized runtime traces but no application source
in the workspace, or want to limit the review to trace evidence.<br/>
**Install:** Base agent only; optional specialist modes are not enabled here.<br/>
**Inputs:** Exact existing workspace trace paths, one scenario and legitimate
sanitization evidence or your direct exact-path confirmation.<br/>
**Expect:** Supported observed metrics and trace citations; source locations,
causes and safe changes remain unknown unless established.<br/>
**Next:** Use [measurement readiness](#measurement-readiness) for missing
correlation/coverage, or authorize a separate scoped source audit.

Before using your own traces, verify they are sanitized. If appropriate, directly
tell the agent in Chat which exact paths you confirm; never endorse placeholders.
Otherwise the agent may ask one batched exact-path question or leave files unread.
Do not inspect payloads simply to discover whether they are safe.

```text
Perform a trace-only audit for this scenario: <task>.
Use only these exact existing workspace artifacts:
<exact trace path 1>
<exact trace path 2, or remove this line>

Do not discover an application, enumerate sibling traces, inspect source,
run commands/workloads or replay requests. Load no optional specialist mode.
Apply the core sanitization gate to each artifact before any payload access.
This template does not confirm sanitization. If eligibility requires confirmation,
ask the permitted one batched exact-path question; no payload access while waiting.
Absent, ambiguous or denied confirmation leaves those paths unread.

If no artifact is eligible, report not auditable with checked paths and no counts
or saved audit. Otherwise cite records and preserve partial coverage.
Distinguish logical calls, attempts, downstream requests, tokens and elapsed
latency only when the evidence supports them. Do not infer request/task success,
safe suppression, source causes or verified code locations from span names/status.
Keep unknowns explicit; do not rank speculative waste or invent savings.

For an auditable result, save one six-section report and Executive Summary under
reports\ without overwrites; verify both and ask before summary preview.
```

For an OTLP JSON export, optionally run the
[metadata importer](offline-tooling.md#import-already-sanitized-otlp-json) yourself
first, then supply the output's exact path with the same eligibility safeguards.
Import does not establish complete capture or create per-request budget measurements.

## Suggested learning path

1. Start with the base source-only audit; read the Executive Summary first.
2. Pick one specialist review only if it answers a specific question.
3. Use recommendation planning for supported fixes; use readiness for evidence gaps.
4. Implement and measure separately under your own approvals.
5. Compare before/after evidence, verify findings and interpret approved gates.

Do not run every template as a checklist. A narrowly scoped answer with clear
unknowns is more useful than repeated broad audits. See
[optional-mode boundaries](agent-guide.md#optional-advisory-reviews) for details.
