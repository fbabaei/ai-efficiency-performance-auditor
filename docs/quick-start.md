# Quick start: AI Efficiency & Performance Auditor

Think of this agent as a **reviewer for your AI application**. It looks for
unnecessary AI/tool calls, repeated work and performance risks, then explains
what to improve and why. It recommends changes; it does not implement them.

**Start with a code review. You do not need traces, Python or every optional
module for your first audit.**

## What changed, in plain language?

Instead of making one large agent do everything, we added optional modules
called **skills**. You install and request only the ones you need.

| Your question | What to use | What you get |
|---|---|---|
| "Where are we doing unnecessary work?" | Base auditor | Findings with evidence and priorities |
| "What should a developer do next?" | `recommendation-planning` | Proposed tasks with safeguards, dependencies, tests and rollback conditions |
| "Could this code change make things worse?" | `change-impact-review` | Focused review of supplied changes and affected code paths |
| "What should we measure?" | `measurement-readiness` | Missing measurements and privacy-conscious instrumentation suggestions |
| "Did the change really fix the finding?" | `audit-comparison`, explicitly requesting finding verification | Fixed, partial, persistent, regressed or inconclusive status, depending on evidence |
| "Are we meeting our approved limits?" | Offline gate, then `efficiency-budget-review` | Calculated checks, followed by a plain-language explanation |
| "Can we use an existing trace export?" | Offline OTLP importer | A metadata-only view of an already-sanitized OpenTelemetry JSON export |

The skills are **checklists for the reviewer**. The offline tools are separate
**calculators you run yourself**. Neither automatically fixes your application.

## 1. Install the base agent

You need VS Code with GitHub Copilot enabled and custom-agent support.

1. Download or clone this repository.
2. Open the **application repository you want to review** in VS Code.
3. Copy the [agent definition](../.github/agents/ai-efficiency-performance-auditor.agent.md)
   from this repository into `.github\agents\` in your application.
4. In Copilot Chat, select **AI Efficiency & Performance Auditor**.
   If it is missing, reload the VS Code window and check the file location.

Keep only the agent definition in that agent directory, not this guide or other
ordinary documentation. Opening the auditor's own repository does not give it
access to a separate application workspace.

## 2. Run your first audit

Choose **one flow**, such as answering a search question or processing an AI
request. Replace the placeholder below with the actual entry-point path in
your application, then paste this into Copilot Chat:

```text
Audit the AI request flow starting at <actual entry-point path>.

Use source code and configuration only. Do not read runtime traces, execute
commands, run workloads or modify application files.

Look for unnecessary tool/model calls, repeated retrieval, retry amplification
and unused results. Explain each demonstrated issue in plain language and
cite the affected code locations. Keep uncertain ideas separate from findings.

Recommend the smallest safe changes and how to validate them.
Save a detailed report and an Executive Summary under reports/ without
overwriting existing files. Ask before opening the summary preview.
```

For example, if your request handler is in `src\search.py`, substitute that
actual path. Start with a small, known flow rather than the whole application.

### Optional: insert a template without copying it

Install the separate [VS Code prompt picker](prompt-picker.md), then press
**Ctrl+Shift+P** and choose **Auditor: Insert Prompt**. Type `/audit-start`,
select it and confirm replacing the Chat draft. The full prompt appears as
editable text; replace the placeholders and send it yourself.

All 14 catalog workflows have picker names. These names work in the picker,
not directly in Copilot's slash menu. The extension does not select the agent,
install skills or confirm trace sanitization. Review attachments before sending.
Its prefill command needs a manual check in your VS Code host.

## 3. Read the result

Normally you receive two Markdown files in the application's `reports\` folder:

- **Executive Summary:** read this first for priorities and next steps.
- **Detailed report:** evidence, call paths, supported measurements, findings,
  proposed changes and a validation plan.

Existing files are preserved. If the host cannot save reports, the agent should
explain that and provide the Markdown in Chat. If it cannot identify an auditable
target, it explains what is missing instead of creating a successful-looking audit.

**A finding is an opportunity, not guaranteed savings.** Check the proposed
change against real workloads and output quality before claiming improvement.

## 4. Add one skill when you need it

For a useful next step, copy the whole
[recommendation-planning directory](../.github/skills/recommendation-planning/)
into `.github\skills\recommendation-planning\` in your application repository.
Select the same auditor agent and request:

```text
Explicitly use recommendation-planning on this existing report only:
<actual detailed audit report path>

Turn supported findings into developer handoff cards. Include the smallest
change, dependencies, safeguards, effort rationale or unknown, proposed tests
and rollback criteria. Do not inspect source to fill gaps or implement changes.
Keep reported locations and savings labeled as supplied, not reverified.
```

You do not select a separate agent for each skill. For other modules, copy their
whole directories too, including any `references\` folder, and explicitly name
the desired mode. Modules do not add execution permissions or extra audit budgets.

Use the [choose-your-goal catalog](usage-prompts.md#choose-your-goal) to find
standalone retrieval, orchestration, service, trace-only, comparison and
report-summary templates as well as the new developer-workflow modules.
Each template lists when to use it, what to install, what to provide, what to
expect and what to do next. See the [full module list](../README.md#optional-advisory-capabilities)
for installation choices.

## 5. Optional: try the offline tools

Skip this section until you want calculated checks or trace import.
You need Python 3.10+ and a terminal opened at the **auditor repository root**,
not the application repository. No package installation is required.

### Try a budget check with synthetic data

This example checks supplied before/after measurements against sample limits:

```powershell
python -m auditor_tools gate .\examples\offline\candidate.json --budgets .\examples\offline\budgets.json --baseline .\examples\offline\baseline.json --confirm-comparable
```

It prints JSON with `"status": "pass"` for the supplied example.
The costs, measurements and approvals are synthetic demonstrations, not
production recommendations or measured application savings.

| Exit code | Meaning |
|---|---|
| 0 | All approved checks pass |
| 1 | At least one supported check fails |
| 2 | Invalid input or a read/write error |
| 3 | More evidence is needed; do not treat this as a pass |

For your application, supply real per-request measurements, including failures,
and actually approved limits. A minimum task-success rate is required: lower
cost is not enough if the application stops doing its job correctly.

### Try importing a sanitized trace

This command uses a synthetic, already-sanitized OpenTelemetry export:

```powershell
python -m auditor_tools import-otlp .\examples\offline\traces.json --confirm-sanitized
```

It prints selected metadata, not prompts or full responses. For your own files,
sanitize them **before** running the tool; the flag is your confirmation, not
an automatic privacy check. Imported spans do not automatically become
per-request budget measurements.

See [offline setup, formats and examples](offline-tooling.md) before using real
measurements, saving output or integrating the exit codes into CI.

## A simple workflow to remember

**Review one flow -> plan a safe change -> implement it yourself -> collect
approved measurements -> compare and verify.**

The auditor does not modify application code, run commands, collect telemetry
or execute benchmarks. It can create new audit reports. These are instruction
boundaries, not a filesystem sandbox; review host tool permissions.
Follow your organization's rules for private code and data: Copilot/model
processing is not guaranteed to be local-only.

The current version is an unreleased candidate. Offline tests validate selected
contracts and calculations, not guaranteed agent behavior or host compatibility.
