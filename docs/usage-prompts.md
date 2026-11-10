# Reusable audit prompts

Open the application repository you want to audit in VS Code and select
**AI Efficiency & Performance Auditor** in Copilot Chat. Install the agent in
`.github\agents\` and the required whole skill directories in `.github\skills\`
inside that application repository, including any bundled references.
See the [installation guide](../README.md#install-in-the-repository-you-want-to-audit).

Copy one prompt below into Chat. Optionally add a known entry-point path and
scenario to reduce discovery. Both prompts use source/configuration only:
runtime traces are not needed. Analysis is advisory, with report-only writes;
it does not execute the application or establish measured performance savings.

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
