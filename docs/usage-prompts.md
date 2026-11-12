# Reusable audit prompts

Open the application repository you want to audit in VS Code and select
**AI Efficiency & Performance Auditor** in Copilot Chat. Install the agent in
`.github\agents\` and the required whole skill directories in `.github\skills\`
inside that application repository, including any bundled references.
See the [installation guide](../README.md#install-in-the-repository-you-want-to-audit).

Copy one prompt below into Chat. Optionally add a known entry-point path and
scenario to reduce discovery. The first-audit and deep-analysis prompts use source/configuration only:
runtime traces are not needed. Analysis is advisory, with report-only writes;
it does not execute the application or establish measured performance savings.

For planning from an existing report rather than a new source audit, use the
[recommendation-planning prompt](#recommendation-planning).

## Recommendation planning

Use this to turn an existing audit into a developer handoff without a new source
audit. Requires `recommendation-planning`. Replace the report placeholder with
an exact existing workspace path, or paste the report directly in Chat.

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

Use this for a bounded PR/diff efficiency review. Requires `change-impact-review`.
Replace the placeholder with an exact existing workspace diff, paste the diff
in Chat, or name both baseline/candidate snapshot paths and their roles.
A PR URL or branch name alone does not provide review evidence.

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

Requires `measurement-readiness`. Supply one entry point/scenario or exact
report. For report-only review, replace the placeholder below.

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

## Finding-level verification

Requires `audit-comparison` including its bundled references. Supply actual
both-side evidence; the prompt does not authorize fetching revisions.

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

Requires `efficiency-budget-review`. Run the [offline companion](offline-tooling.md)
yourself first. Confirm exact-path sanitization in Chat for any runtime artifacts;
this template is not confirmation until you endorse the actual paths.

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

Use this for an initial review of one representative request and its tool/model
efficiency. Requires `orchestration-efficiency-review` and
`context-retrieval-review`.

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

Use this to examine the same bounded request more deeply, including failure
recovery and service lifecycle behavior. Requires
`orchestration-efficiency-review`, `context-retrieval-review` and
`service-performance-review`. More specialized checks do not expand permissions
or exploration budgets, or imply exhaustive application coverage.

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

Neither prompt enables `audit-comparison`. Request that mode separately when
you have named baseline/candidate reports, existing snapshots or eligible
sanitized evidence. See [optional advisory reviews](agent-guide.md#optional-advisory-reviews).
