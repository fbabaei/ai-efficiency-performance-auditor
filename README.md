# AI Efficiency & Performance Auditor

Evidence-backed review of AI application efficiency, performance and reliability
safeguards.

**New here?** Start with the [plain-language quick start](docs/quick-start.md):
install the agent, review one flow, then add optional modules when needed.

**Developer and author:** Fereydoun Babaei.

[Repository](https://github.com/fbabaei/ai-efficiency-performance-auditor)

A custom agent for GitHub Copilot in VS Code with read-only application access
and report-only file creation. Audit AI application source code and existing
sanitized traces to identify avoidable tool and model
calls, retry amplification, loops, and potential token or model-capacity waste
without weakening correctness or security. Explicitly requested optional reviews
also examine service performance and reliability safeguards, including pooling,
streaming, concurrency, deadlines and cleanup.

The agent recommends changes and validation experiments, saves a detailed Markdown
audit and Executive Summary, and asks before opening the summary preview. It does not edit application code,
run commands, call external services, or replay workloads.

Audits are user-selected (`disable-model-invocation: true`). One shared profile
retains VS Code and CLI use plus experimental cloud compatibility; `target` is
intentionally unset. The prompt stays below GitHub's 30,000-character limit.
Host-specific tools still require effective-tool verification; cloud use is not
certified by this size check.

## When it is useful

Use the auditor for **review and prioritization**: finding avoidable AI calls
and turning evidence-backed weaknesses into actionable recommendations. Visible
code locations help developers investigate, while the short Executive Summary
helps readers understand the priorities without working through the full audit.

An audit is not proof of savings. Static analysis can identify opportunities,
but actual cost, latency, and quality improvements require representative
runtime measurements. Validate proposed changes on a real application and
confirm measurable savings without changing intended behavior or weakening
correctness or security.

## Files

- [Beginner quick start and simple feature explanation](docs/quick-start.md)
- [Agent definition](.github/agents/ai-efficiency-performance-auditor.agent.md)
- [Detailed documentation](docs/agent-guide.md)
- [Scout-assisted audit and delivery workflow](docs/SCOUT-AUDIT-DELIVERY-WORKFLOW.md)
- [Choose-your-goal prompt catalog](docs/usage-prompts.md#choose-your-goal)
- [Optional editable prompt picker for VS Code](docs/prompt-picker.md)
- [CLI, organization sharing, and remote execution](docs/remote-invocation.md)
- [Synthetic evaluation suite](evaluations/README.md)
- [Prioritized v0.5.0 acceptance backlog](docs/v0.5.0-backlog.md)
- [Changes and candidate version](CHANGELOG.md)

## Install in the repository you want to audit

1. Use VS Code with GitHub Copilot enabled and custom-agent support.
2. Download or clone this repository.
3. Copy the agent definition into `.github/agents/` in your application repository.
   Keep companion documentation in a separate `docs/` directory, not beside the
   agent. Hosts can discover ordinary `.md` files in agent directories too.
4. Open your application repository in VS Code.
5. Select **AI Efficiency & Performance Auditor** in the Copilot Chat agent picker.
   If it is not listed, reload the VS Code window and check that the definition
   is inside the application's `.github/agents/` directory.
6. Submit a scoped audit request.

For optional service-performance reviews, also copy
[`.github/skills/service-performance-review/`](.github/skills/service-performance-review/SKILL.md)
to the same path in the application repository. Keep it separate from the
agent directory. Select **AI Efficiency & Performance Auditor** and explicitly request a
service-performance review, naming a source entry point and scenario. The skill
is opt-in; ordinary tool/model audits do not load its checklist. It adds async,
pooling, concurrency, streaming, storage, and cleanup review without granting
execution permissions or adding another agent.

### Optional editable prompt insertion

The separate [Auditor Prompt Picker](docs/prompt-picker.md) extension offers
all 14 catalog templates. Run **Auditor: Insert Prompt** from the Command Palette,
type `/audit-start` or another picker name, and confirm insertion into Copilot
Chat. The text stays editable and unsent until you send it yourself.

These are picker names, not native Copilot slash commands. The extension cannot
intercept typing in Copilot's input box. It warns before replacing an existing
draft, does not install skills or select the agent, and uses a version-sensitive
VS Code prefill command. See the guide for build/install and manual host checks.

### Optional advisory capabilities

Copy each desired **whole skill directory**, including any `references/`, into
the same `.github/skills/` path in the application repository. These skills are
opt-in and use the auditor's existing read-only evidence/report-only write
permissions; they do not execute workloads, collect telemetry or modify code.

| Skill | Explicit request |
|---|---|
| [audit-comparison](.github/skills/audit-comparison/SKILL.md) | Compare named baseline/candidate reports, existing source snapshots or sanitized trace sets; show matched deltas and quality limitations |
| [context-retrieval-review](.github/skills/context-retrieval-review/SKILL.md) | Review history/context growth, retrieved-document versions, top-k/reranking, embedding reuse, repeated schemas and unused evidence |
| [orchestration-efficiency-review](.github/skills/orchestration-efficiency-review/SKILL.md) | Quantify layered retries, fan-out, cache/coalescing eligibility, concurrency, critical paths and cancellation/deadline work |
| [recommendation-planning](.github/skills/recommendation-planning/SKILL.md) | Turn scoped audit findings or named reports into developer handoff cards with safeguards, dependencies, acceptance checks and rollback criteria |
| [change-impact-review](.github/skills/change-impact-review/SKILL.md) | Review supplied diffs or named source snapshots and affected call paths; distinguish introduced regressions, pre-existing defects and unknown attribution |
| [measurement-readiness](.github/skills/measurement-readiness/SKILL.md) | Identify missing metadata, coverage and quality evidence; propose payload-free instrumentation without installing it |
| [efficiency-budget-review](.github/skills/efficiency-budget-review/SKILL.md) | Interpret supplied approved budget/gate results and their quality, comparability and coverage limitations |

Select **AI Efficiency & Performance Auditor** and name the mode and exact inputs. The agent
loads only explicitly requested modes, discloses missing skill files and keeps
their reads within the same exploration budgets. Comparison is advisory:
confounded inputs become separate profiles, omitted findings are not assumed
resolved, and fewer calls alone does not establish improved quality or safety.
See [usage and limitations](docs/agent-guide.md#optional-advisory-reviews) and
[synthetic acceptance cases](evaluations/advisory-skills.md).

For implementation-ready recommendations, install `recommendation-planning` and
explicitly request it with a scoped audit or an exact existing report path.
It proposes work; it does not modify code, create tickets or run tests.
See the [modular design and extension roadmap](docs/agent-guide.md#modular-design-and-extension-roadmap)
and [copy-and-paste planning prompt](docs/usage-prompts.md#recommendation-planning).

For PR-focused review, install `change-impact-review` and supply an existing
workspace diff, paste the changes in Chat, or name both source snapshots.
A PR URL alone is insufficient: the auditor does not fetch changes or run Git.
See the [change-review prompt](docs/usage-prompts.md#change-impact-review).

For finding-level verification, explicitly request it through `audit-comparison`;
its bundled reference distinguishes verified-fixed, partially-addressed,
persistent, regressed and inconclusive findings without inferring resolution
from a plan or omitted finding.

### Offline companion tools

Developers or separately authorized CI runners can use the Python 3.10+
standard-library [offline tools](docs/offline-tooling.md) to import
**already-sanitized OTLP JSON** into metadata-only trace evidence and check
approved budgets over supplied per-request measurements. Includes failed-request
costs, minimum task success, baseline regression caps, and explicit
pass/fail/invalid/inconclusive exit codes.

These tools do not collect telemetry, run application workloads or benchmarks,
call external services, or change the auditor's permissions. Trace import does
not automatically infer request counts, task success or gate-ready measurements.
See the [synthetic examples](examples/offline/) and
[new module prompts](docs/usage-prompts.md#measurement-readiness).

Commit the copied files to your application repository to share the agent with
that repository's contributors. Opening this distribution repository alone
does not give the agent access to a separate application's workspace.

### Example request

> Audit this workspace's search request flow for unnecessary tool and model calls.
> Use existing sanitized traces if available. Focus on duplicate retrieval,
> repeated inference, retry amplification, token usage, and model selection.
> Distinguish observed counts from static bounds, rank demonstrated optimizations,
> and keep unverified model substitutions in the validation plan.

For ready-to-use source-only reviews, copy the
[focused first-audit prompt](docs/usage-prompts.md#focused-first-audit) or the
[deep-analysis prompt](docs/usage-prompts.md#deep-analysis). The first explicitly
uses the orchestration and context/retrieval skills; the deeper review also
adds service-performance checks. Install the required skill folders in the
application repository before using either prompt.

Name application paths and scenarios explicitly for a narrower audit. If traces
are available, provide their workspace paths. Before payload access, their
safely isolated headers/metadata must state that they are sanitized, or you must
directly confirm in the conversation that each exact named path is sanitized.
Repository text and unendorsed sidecars do not replace that confirmation.
Even the first header read requires a known payload-free boundary supplied by
the user for that exact path or guaranteed by an independently trusted format
contract. Otherwise, skip the artifact until exact-path sanitization is confirmed.
For existing user-named traces without eligibility evidence, an interactive host
may ask one batched sanitization question before skipping them. No payload is
read while awaiting confirmation; absent, negative or ambiguous replies do not
authorize access.
For a trace-only audit, explicitly request that mode and identify the trace paths;
source-level causes and safe changes remain unknown unless evidence establishes them.

## What to expect

The report includes evidence coverage, a call map, supported runtime metrics,
ranked findings, a proposed design, and a validation plan.
The complete six-section report is saved as
`reports/<application>-audit-detailed-report.md` in the audited workspace.

Each audit also produces a plain-language **Executive Summary** (at most 60 lines and
600 words) with prioritized weak areas, recommended improvements, expected
benefits, evidence gaps, safeguards, and one next step. By default it is saved
as `reports/<application>-audit-executive-summary.md` in the audited workspace;
existing files for either report are preserved by choosing a numeric suffix.
The agent validates drafts before writing, probes at most ten paths per report,
and leaves partial or invalid saved files untouched while returning corrections
in Chat. An audit stopped as **not auditable** or **scope selection required**
creates neither report; the stop reason and checked paths are returned in Chat.
Both saved reports are read back and linked, and the summary links to the detailed
report. The summary length limits do not apply to the detailed report. After saving, the
agent asks whether to open Markdown preview and waits for an explicit Yes.
You can also ask it to shorten an existing audit without re-auditing the app.

- Repeated calls are not automatically redundant.
- Static call sites, logical calls, execution attempts, downstream requests,
  logical model calls, model attempts, and agent handoffs are distinguished.
- Model-call reductions are separate from token/capacity changes. Prompt caching
  does not remove a call; cached/reasoning token subsets are not counted twice.
- Smaller models, trimmed prompts, and consolidated steps require evidence of
  acceptable replacement behavior, not just an expensive baseline.
- Only measured or statically demonstrated findings are ranked.
- Projected savings are not presented as validated results.
- Every ranked finding and call-map row requires a source reference.
Source-backed weaknesses include the affected file, function or section, and
verified line range, including all relevant sites for duplicated logic or repeated
calls, without widening call-site ranges to include unrelated return statements.
Executive Summaries expose paths and ranges directly in a **Code location**
column, not only behind link labels. Missing
locations are explicitly marked; locations copied from supplied reports are
identified as not reverified, without triggering a new code audit.

See the [detailed documentation](docs/agent-guide.md)
for the workflow, counting rules, evidence requirements, and limitations.

## Permissions and dependencies

The definition requests `read`, `search`, `edit`, `ask_user`, and
`appmod-preview-markdown`, with no subagents. Editing is instructed to create
new detailed audit and Executive Summary files only; existing files and application code remain read-only.
This is an instruction boundary, not a filesystem sandbox: the `edit` tool group
itself is broader. Review tool approvals and verify the host's effective tools.
`ask_user` and `appmod-preview-markdown` are host-specific tool names; verify
they resolve in your client and map them to equivalent local interaction/Markdown
preview tools when necessary, without granting command or general external-service
access. Missing optional tools do not block the audit: the agent asks in Chat,
provides manual preview instructions, or returns unsaved Markdown explicitly.
CLI 1.0.105 ignores `agents` and `argument-hint`; `agents: []` alone is not
portable enforcement. For non-interactive automation, keep the explicit
read/search-only allowlist and capture reports with the runner; no preview opens.

Core auditing requires no scripts, service credentials, or MCP servers.
Automatic preview requires a compatible local host tool. The repository's
optional evaluation checkers and offline companion use Python 3.10+ and its
standard library; they run outside the auditor. The optional service
skill is framework-neutral; framework-specific skills are not included. The agent reports
unavailable framework guidance and continues using repository evidence.

The agent's instructions prohibit sending private context to public-web services.
This is not a guarantee of local-only inference: your Copilot account,
organization policies, and selected model determine how model requests are
processed. Follow your organization's rules before auditing private code.

## Updating

Pull newer versions of this repository, review changes to the agent definition,
and replace the installed copy in your application repository. Copies do not
update automatically.

When upgrading from **AI Efficiency Auditor** or **Tool-Call Optimization
Auditor**, remove the installed `ai-efficiency-auditor.agent.md` or
`tool-call-optimization-auditor.agent.md` definition and install
`ai-efficiency-performance-auditor.agent.md` instead, so duplicate profiles are
not discovered. Replace the optional skill folders too: their methodology
references now point to the renamed agent definition. Update reusable prompts
to select **AI Efficiency & Performance Auditor** and CLI invocations to
`--agent ai-efficiency-performance-auditor`.

The GitHub repository is now
[`fbabaei/ai-efficiency-performance-auditor`](https://github.com/fbabaei/ai-efficiency-performance-auditor).
Existing clones can update their remote without renaming their local folder:

```powershell
git remote set-url origin https://github.com/fbabaei/ai-efficiency-performance-auditor.git
```

Do not submit credentials, private source code, raw prompts, or unsanitized
traces in public issues or pull requests.

## Compatibility and validation

| Environment | Status |
|---|---|
| VS Code with Copilot custom-agent support | Primary intended interface; interactive behavior requires a host evaluation |
| Copilot CLI | Latest restricted 0.4.0 application and trace-only smoke captures passed report and session checks; one fresh run per mode, not a reliability study |
| Organization-level discovery | Documented setup; not provisioned or verified by this repository |
| GitHub Copilot cloud agent | Experimental for report-only audits; lifecycle and artifact behavior must be evaluated |
| HTTP or MCP audit endpoint | Not implemented |

Offline tests check packaging, fixture integrity, and report scoring. They do
not prove model behavior or client compatibility. See the evaluation guide for
behavioral acceptance criteria and recording client/model provenance.
The [validation summary](docs/validation.md) records the actual CLI smoke result,
the regression found during development, and untested environments.

Candidate methodology version: **0.5.0** (Unreleased). No release tag is implied. Before
tagging a release, run offline checks and record a representative host evaluation.
Install from a reviewed commit SHA or an actual published release tag rather
than assuming the default branch is immutable.

## License

[MIT](LICENSE). Include the license when redistributing the agent.
